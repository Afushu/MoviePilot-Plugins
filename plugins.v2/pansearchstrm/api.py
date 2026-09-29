"""网盘搜索 STRM 插件的 HTTP 接口。"""

from typing import Any, Dict, List, Optional

from fastapi import Body, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.runtime.log import logger

from .core.p115 import P115Error
from .search.models import PanResourceItem
from .search.telegram import TelegramSearcher


class SearchRequest(BaseModel):
    """网盘搜索请求体。"""

    keyword: str = ""
    sources: List[str] = []


class TransferRequest(BaseModel):
    """转存并生成 STRM 的请求体。"""

    source: str = ""
    title: str = ""
    share_url: str = ""
    access_code: str = ""
    resource_type: str = ""
    size_text: str = ""
    pubdate: str = ""
    channel: str = ""
    sub_path: str = ""
    extra: Dict[str, Any] = {}


class TelegramWaitRequest(BaseModel):
    """Telegram 扫码等待请求体。"""

    password: str = ""


class CookieRequest(BaseModel):
    """115 Cookie 手动设置请求体。"""

    cookies: str = ""


class LinkRequest(BaseModel):
    """115 分享链接请求体。"""

    url: str = ""
    cid: int = 0
    file_ids: List[str] = []
    title: str = ""
    sub_path: str = ""
    target_path: str = ""


class RecordRemoveRequest(BaseModel):
    """转存记录移除请求体。"""

    index: int = 0


class PanSearchApi:
    """聚合插件对外接口，所有状态都从主插件实例读取。"""

    def __init__(self, plugin: Any) -> None:
        """保存主插件实例引用。"""
        self._plugin = plugin

    def status(self) -> Dict[str, Any]:
        """返回插件当前状态，供 Vue 页面初始化。"""
        config = self._plugin.get_config_model()
        client = self._plugin.get_115_client()
        authorized = False
        account = ""
        if client.is_authorized:
            authorized, account = client.check_login()
        return {
            "success": True,
            "enabled": self._plugin.get_state(),
            "search_inject_enabled": bool(config.search_inject_enabled),
            "sources": self._plugin.aggregator().enabled_sources(),
            "p115": {
                "authorized": authorized,
                "account": account,
                "receive_path": config.p115.receive_path,
                "share_duration": config.p115.share_duration,
            },
            "telegram": {
                "authorized": bool(self._plugin.get_telegram_session()),
                "channels": list(config.telegram.channels),
            },
            "strm": {
                "output_path": config.strm.output_path,
                "url_mode": config.strm.url_mode,
            },
        }

    def get_config(self) -> Dict[str, Any]:
        """读取插件配置。"""
        return {"success": True, "config": self._plugin.get_config_model().model_dump()}

    def save_config(self, payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
        """保存插件配置。"""
        try:
            config = self._plugin.save_config_model(payload or {})
        except Exception as error:  # noqa: BLE001
            return {"success": False, "message": f"配置保存失败：{error}"}
        return {"success": True, "config": config.model_dump()}

    def qrcode_115(self) -> Dict[str, Any]:
        """获取 115 扫码登录二维码。"""
        try:
            token = self._plugin.get_115_client().qrcode_token()
        except P115Error as error:
            return {"success": False, "message": str(error)}
        image = ""
        try:
            import base64
            import io

            import qrcode

            buffer = io.BytesIO()
            content = str(token.get("qrcode") or "")
            if not content:
                content = f"https://115.com/scan/dg-{token.get('uid')}"
            qrcode.make(content, box_size=10, border=4).save(buffer, format="PNG")
            image = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
        except Exception as error:  # noqa: BLE001 - 图片生成失败仍返回原始内容
            logger.error(f"生成 115 二维码图片失败：{error}")
        self._plugin.save_115_pending(token)
        return {
            "success": True,
            "uid": token.get("uid"),
            "app": token.get("app"),
            "qr_image": image,
            "qr_content": token.get("qrcode"),
            "tips": "请使用 115 客户端扫描二维码登录",
        }

    def qrcode_115_status(self) -> Dict[str, Any]:
        """轮询 115 扫码状态，成功后写入登录凭据。"""
        pending = self._plugin.get_115_pending()
        if not pending:
            return {"success": False, "status": "expired", "message": "请先获取二维码"}
        result = self._plugin.get_115_client().qrcode_status(
            uid=str(pending.get("uid") or ""),
            time_value=pending.get("time"),
            sign=str(pending.get("sign") or ""),
            app=str(pending.get("app") or "web"),
        )
        if result.get("status") == "confirmed":
            self._plugin.persist_115_cookies(str(result.get("cookies") or ""))
            self._plugin.clear_115_pending()
            result.pop("cookies", None)
        return {"success": True, **result}

    def browse_115(self, path: str = Query(""), cid: int = Query(-1)) -> Dict[str, Any]:
        """浏览 115 网盘目录，供转存目录选择使用。"""
        client = self._plugin.get_115_client()
        if not client.is_authorized:
            return {"success": False, "message": "115 未授权，请先扫码登录"}
        try:
            if cid is None or int(cid) < 0:
                folder_id = client.ensure_folder(path) if path else 0
            else:
                folder_id = int(cid)
            entries = client.list_folder(folder_id)
        except P115Error as error:
            return {"success": False, "message": str(error)}
        folders = [item for item in entries if item.get("is_dir")]
        return {
            "success": True,
            "cid": folder_id,
            "path": path,
            "folders": [
                {
                    "fid": str(item.get("fid") or ""),
                    "name": str(item.get("name") or ""),
                }
                for item in folders
            ],
        }

    def qrcode_telegram(self) -> Dict[str, Any]:
        """获取 Telegram 扫码登录链接。"""
        searcher = self._plugin.build_telegram_searcher()
        result = searcher.qr_start()
        url = str(result.get("url") or "")
        if not url:
            return {"success": False, "message": result.get("message") or "获取失败"}
        image = ""
        try:
            import base64
            import io

            import qrcode

            buffer = io.BytesIO()
            qrcode.make(url).save(buffer, format="PNG")
            image = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
        except Exception as error:  # noqa: BLE001
            logger.error(f"生成 Telegram 二维码图片失败：{error}")
        return {"success": True, "url": url, "qr_image": image}

    def telegram_wait(self, payload: TelegramWaitRequest = Body(...)) -> Dict[str, Any]:
        """等待 Telegram 扫码结果并保存登录会话。"""
        searcher = self._plugin.build_telegram_searcher()
        result = searcher.qr_wait(password=payload.password)
        if result.get("status") == "confirmed":
            self._plugin.persist_telegram_session(str(result.get("session") or ""))
            result.pop("session", None)
        return {"success": result.get("status") != "error", **result}

    def search(self, payload: SearchRequest = Body(...)) -> Dict[str, Any]:
        """搜索网盘资源。"""
        keyword = str(payload.keyword or "").strip()
        if not keyword:
            return {"success": False, "message": "搜索关键词不能为空"}
        items = self._plugin.aggregator().search(keyword, payload.sources)
        return {
            "success": True,
            "keyword": keyword,
            "total": len(items),
            "results": [item.to_dict() for item in items],
        }

    def transfer(self, payload: TransferRequest = Body(...)) -> Dict[str, Any]:
        """转存选中的资源、生成长期分享并落地 STRM。"""
        item = PanResourceItem(
            source=payload.source,
            title=payload.title,
            share_url=payload.share_url,
            access_code=payload.access_code,
            resource_type=payload.resource_type,
            size_text=payload.size_text,
            pubdate=payload.pubdate,
            channel=payload.channel,
            extra=dict(payload.extra or {}),
        )
        try:
            result = self._plugin.transfer_item(item, payload.sub_path)
        except P115Error as error:
            return {"success": False, "message": str(error)}
        except Exception as error:  # noqa: BLE001
            logger.error(f"网盘转存失败：{error}")
            return {"success": False, "message": f"转存失败：{error}"}
        return {"success": True, **result}

    def records(self) -> Dict[str, Any]:
        """返回插件累计的转存记录。"""
        records = self._plugin.get_data("records") or []
        return {"success": True, "total": len(records), "records": records}

    def remove_record(self, payload: RecordRemoveRequest = Body(...)) -> Dict[str, Any]:
        """按索引移除一条转存记录。"""
        records = list(self._plugin.get_data("records") or [])
        index = int(payload.index)
        if index < 0 or index >= len(records):
            return {"success": False, "message": "记录不存在"}
        records.pop(index)
        self._plugin.save_data("records", records)
        return {"success": True, "total": len(records), "records": records}

    def get_cookie(self) -> Dict[str, Any]:
        """返回 115 登录状态与脱敏后的 Cookie。"""
        client = self._plugin.get_115_client()
        raw = client.cookies
        masked = ""
        if raw:
            parts = [item.strip() for item in raw.split(";") if item.strip()]
            masked = "; ".join(
                f"{item.split('=', 1)[0]}=***" if "=" in item else item
                for item in parts
            )
        authorized, account = (False, "")
        if client.is_authorized:
            authorized, account = client.check_login()
        return {
            "success": True,
            "has_cookie": bool(raw),
            "cookie_masked": masked,
            "authorized": authorized,
            "account": account,
        }

    def set_cookie(self, payload: CookieRequest = Body(...)) -> Dict[str, Any]:
        """手动写入 115 登录 Cookie。"""
        text = str(payload.cookies or "").strip()
        if not text:
            return {"success": False, "message": "Cookie 不能为空"}
        self._plugin.persist_115_cookies(text)
        client = self._plugin.get_115_client()
        authorized, account = client.check_login()
        return {
            "success": True,
            "authorized": authorized,
            "account": account,
            "message": "Cookie 已保存" if authorized else "Cookie 已保存，但校验未通过",
        }

    def link_preview(self, payload: LinkRequest = Body(...)) -> Dict[str, Any]:
        """解析分享链接并返回根目录条目。"""
        try:
            data = self._plugin.transfer_pipeline().preview(payload.url)
        except P115Error as error:
            return {"success": False, "message": str(error)}
        except Exception as error:  # noqa: BLE001
            logger.error(f"解析分享链接失败：{error}")
            return {"success": False, "message": f"解析失败：{error}"}
        return {"success": True, **data}

    def link_browse(self, payload: LinkRequest = Body(...)) -> Dict[str, Any]:
        """浏览分享中的指定目录。"""
        try:
            data = self._plugin.transfer_pipeline().browse(
                payload.url, int(payload.cid or 0)
            )
        except P115Error as error:
            return {"success": False, "message": str(error)}
        except Exception as error:  # noqa: BLE001
            return {"success": False, "message": f"读取目录失败：{error}"}
        return {"success": True, **data}

    def link_transfer(self, payload: LinkRequest = Body(...)) -> Dict[str, Any]:
        """仅转存分享中的选中条目。"""
        try:
            data = self._plugin.transfer_pipeline().transfer_only(
                url=payload.url,
                file_ids=payload.file_ids,
                sub_path=payload.sub_path,
                target_path=payload.target_path,
            )
        except P115Error as error:
            return {"success": False, "message": str(error)}
        except Exception as error:  # noqa: BLE001
            logger.error(f"转存失败：{error}")
            return {"success": False, "message": f"转存失败：{error}"}
        return {"success": True, **data}

    def link_strm(self, payload: LinkRequest = Body(...)) -> Dict[str, Any]:
        """转存后生成长期分享并写出 STRM。"""
        try:
            data = self._plugin.transfer_pipeline().publish(
                url=payload.url,
                file_ids=payload.file_ids,
                title=payload.title,
                sub_path=payload.sub_path,
            )
        except P115Error as error:
            return {"success": False, "message": str(error)}
        except Exception as error:  # noqa: BLE001
            logger.error(f"生成 STRM 失败：{error}")
            return {"success": False, "message": f"生成 STRM 失败：{error}"}
        self._plugin.remember_record(
            {
                "source": "link",
                "title": data.get("title") or payload.title or payload.url,
                "share_url": payload.url,
                "result": data,
            }
        )
        return {"success": True, **data}

    def redirect(
        self,
        share_code: str = Query(...),
        receive_code: str = Query(""),
        file_id: str = Query(...),
        file_name: str = Query(""),
    ) -> Any:
        """把 STRM 请求 302 重定向到 115 直链。"""
        try:
            url = self._plugin.get_115_client().share_download_url(
                share_code=share_code,
                receive_code=receive_code,
                file_id=file_id,
            )
        except Exception as error:  # noqa: BLE001
            logger.error(f"解析分享直链失败：{error}")
            return {"success": False, "message": str(error)}
        return RedirectResponse(url=url, status_code=302)

"""网盘资源处理流水线：目录浏览 → 转存 → 长期分享 → 生成 STRM。"""

from typing import Any, Dict, List, Optional

from app.runtime.log import logger

from ..core.config import PanSearchStrmConfig
from ..core.p115 import P115Error, Pan115Client
from ..core.utils import extract_share_payload
from ..search.models import PanResourceItem
from .strm import StrmWriter, is_media_file


def human_size(size: Any) -> str:
    """把字节数转换为便于阅读的容量文本。"""
    try:
        value = float(size or 0)
    except (TypeError, ValueError):
        return str(size or "")
    if value <= 0:
        return ""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024.0
        index += 1
    return f"{value:.2f}{units[index]}"


class TransferPipeline:
    """把网盘分享里的资源落地为本地 STRM，并保留可复用的中间结果。"""

    def __init__(self, config: PanSearchStrmConfig, client: Pan115Client) -> None:
        """保存插件配置与已授权的 115 客户端。"""
        self._config = config
        self._client = client

    @property
    def _extensions(self) -> List[str]:
        """返回配置中的媒体扩展名列表。"""
        text = str(self._config.strm.media_ext or "")
        return [item.strip() for item in text.split(",") if item.strip()]

    def parse_link(self, url: str) -> Dict[str, str]:
        """解析 115 分享链接，返回分享码与提取码。"""
        payload = extract_share_payload(url)
        if not payload.get("share_code"):
            raise P115Error("未识别到 115 分享链接，请检查链接格式")
        return payload

    def preview(self, url: str) -> Dict[str, Any]:
        """预览分享链接：返回标题、根目录条目与容量信息。"""
        payload = self.parse_link(url)
        share_code = payload["share_code"]
        receive_code = payload.get("receive_code") or ""
        info = self._client.share_info(share_code, receive_code)
        entries = info.get("entries") or []
        return {
            "share_code": share_code,
            "receive_code": receive_code,
            "share_link": self._client.build_share_link(share_code, receive_code),
            "title": info.get("title") or "",
            "count": info.get("count") or 0,
            "size": info.get("size") or 0,
            "size_text": human_size(info.get("size")),
            "entries": [self._entry_view(item) for item in entries],
        }

    def browse(self, url: str, cid: int = 0) -> Dict[str, Any]:
        """浏览分享中指定目录的条目，供文件列表查看。"""
        payload = self.parse_link(url)
        result = self._client.share_entries(
            payload["share_code"], payload.get("receive_code") or "", cid
        )
        return {
            "share_code": payload["share_code"],
            "receive_code": payload.get("receive_code") or "",
            "cid": result["cid"],
            "size_text": human_size(result["total_size"]),
            "entries": [self._entry_view(item) for item in result["entries"]],
        }

    def transfer_only(
        self,
        url: str,
        file_ids: Optional[List[str]] = None,
        sub_path: str = "",
        target_path: str = "",
    ) -> Dict[str, Any]:
        """只做转存：把分享中的选中条目保存到网盘目标目录。"""
        payload = self.parse_link(url)
        share_code = payload["share_code"]
        receive_code = payload.get("receive_code") or ""
        folder_path = target_path or self._config.p115.receive_path
        folder_id = self._client.ensure_folder(folder_path)
        entries = self._client.list_share(share_code, receive_code)
        targets = self._select(entries, file_ids)
        if not targets:
            raise P115Error("分享中没有可转存的媒体文件")
        transfer_ids = [str(item.get("fid") or "") for item in targets]
        self._client.transfer(share_code, receive_code, transfer_ids, folder_id)
        logger.info(f"已转存 {len(transfer_ids)} 个条目到 {folder_path}")
        return {
            "share_code": share_code,
            "target_path": folder_path,
            "target_cid": folder_id,
            "transferred": len(transfer_ids),
            "entries": [self._entry_view(item) for item in targets],
            "sub_path": sub_path,
        }

    def publish(
        self,
        url: str,
        file_ids: Optional[List[str]] = None,
        title: str = "",
        sub_path: str = "",
    ) -> Dict[str, Any]:
        """转存后生成长期分享，并把每个媒体文件写成 STRM。"""
        payload = self.parse_link(url)
        share_code = payload["share_code"]
        receive_code = payload.get("receive_code") or ""
        info = self._client.share_info(share_code, receive_code)
        folder_id = self._client.ensure_folder(self._config.p115.receive_path)
        entries = self._client.list_share(share_code, receive_code)
        targets = self._select(entries, file_ids)
        if not targets:
            raise P115Error("分享中没有可转存的媒体文件")
        transfer_ids = [str(item.get("fid") or "") for item in targets]
        self._client.transfer(share_code, receive_code, transfer_ids, folder_id)
        logger.info(
            f"已转存 {len(transfer_ids)} 个条目到 {self._config.p115.receive_path}"
        )

        local_ids = self._resolve_local_ids(folder_id, targets)
        share = self._client.create_share(
            local_ids,
            duration=self._config.p115.share_duration,
            auto_renewal=self._config.p115.auto_renewal,
        )
        new_share_code = share["share_code"]
        new_receive_code = share.get("receive_code", "")
        media_files = self._client.iter_share_media(
            new_share_code, new_receive_code, self._extensions
        )
        if not media_files:
            raise P115Error("转存内容中没有找到可生成 STRM 的媒体文件")

        writer = self._writer()
        media_title = title or info.get("title") or new_share_code
        share_link = self._client.build_share_link(new_share_code, new_receive_code)
        records: List[Dict[str, Any]] = []
        for media in media_files:
            url_text = writer.build_url(
                share_code=new_share_code,
                receive_code=new_receive_code,
                file_id=media["fid"],
                file_name=media["name"],
                share_link=share_link,
            )
            path = writer.write(
                title=media_title,
                file_name=media["name"],
                url=url_text,
                sub_path="/".join(
                    part for part in (sub_path, media.get("dir") or "") if part
                ),
            )
            records.append(
                {
                    "name": media["name"],
                    "dir": media.get("dir") or "",
                    "size_text": human_size(media.get("size")),
                    "strm_path": path,
                    "share_code": new_share_code,
                    "receive_code": new_receive_code,
                    "file_id": media["fid"],
                }
            )
        summary = writer.summary(records)
        summary.update(
            {
                "title": media_title,
                "share_link": share_link,
                "share_code": new_share_code,
                "receive_code": new_receive_code,
                "duration": self._config.p115.share_duration,
                "target_path": self._config.p115.receive_path,
            }
        )
        return summary

    def run(
        self,
        item: PanResourceItem,
        sub_path: str = "",
        file_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """处理一条搜索结果：必要时先兑换聚影票据，再走完整流水线。"""
        url = item.share_url
        if item.source == "juying" and not extract_share_payload(url).get("share_code"):
            from ..search.juying import JuyingSearcher

            resolved = JuyingSearcher(self._config.juying).resolve(item)
            url = resolved.share_url
        if item.access_code and "password=" not in url:
            url = f"{url}?password={item.access_code}"
        return self.publish(
            url=url,
            file_ids=file_ids,
            title=item.title or "",
            sub_path=sub_path,
        )

    def _select(
        self, entries: List[Dict[str, Any]], file_ids: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """挑选需要转存的条目：指定 id 优先，否则按媒体扩展名过滤。"""
        wanted = {str(value) for value in (file_ids or []) if str(value).strip()}
        result: List[Dict[str, Any]] = []
        for entry in entries:
            identifier = str(entry.get("fid") or "")
            name = str(entry.get("name") or "")
            if wanted:
                if identifier in wanted:
                    result.append(entry)
                continue
            if entry.get("is_dir") or is_media_file(name, self._extensions):
                result.append(entry)
        return result

    def _resolve_local_ids(
        self, folder_id: int, targets: List[Dict[str, Any]]
    ) -> List[str]:
        """把分享内的条目 id 映射为网盘本地 id，冲突改名时按名称兜底。"""
        local: Dict[str, str] = {}
        try:
            for item in self._client.list_folder(folder_id):
                name = str(item.get("n") or item.get("name") or "").strip()
                identifier = str(item.get("fid") or item.get("file_id") or "")
                if name and identifier:
                    local[name] = identifier
        except P115Error as error:
            logger.warning(f"读取转存目录失败，直接复用分享内的文件 id：{error}")
        resolved: List[str] = []
        for entry in targets:
            name = str(entry.get("name") or "").strip()
            share_id = str(entry.get("fid") or "")
            resolved.append(local.get(name) or share_id)
        return [item for item in resolved if item]

    def _writer(self) -> StrmWriter:
        """按配置构造 STRM 写入器。"""
        return StrmWriter(
            output_path=self._config.strm.output_path,
            redirect_base=self._resolve_address(self._config.moviepilot_address),
            url_mode=self._config.strm.url_mode,
            overwrite=self._config.strm.overwrite,
        )

    @staticmethod
    def _resolve_address(configured: str) -> str:
        """优先使用插件配置的访问地址，缺省时回落到 MoviePilot 的 APP_DOMAIN。"""
        text = str(configured or "").strip()
        if text:
            return text
        try:
            from app.runtime.config import settings

            return str(getattr(settings, "APP_DOMAIN", "") or "").strip()
        except Exception:  # noqa: BLE001 - 配置不可用时返回空串
            return ""

    @staticmethod
    def _entry_view(entry: Dict[str, Any]) -> Dict[str, Any]:
        """把条目转换为接口返回结构。"""
        return {
            "fid": str(entry.get("fid") or ""),
            "name": str(entry.get("name") or ""),
            "is_dir": bool(entry.get("is_dir")),
            "size": int(entry.get("size") or 0),
            "size_text": human_size(entry.get("size")),
            "pickcode": str(entry.get("pickcode") or ""),
        }

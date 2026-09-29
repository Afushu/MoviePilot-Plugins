"""115 网盘能力封装：扫码授权、目录管理、转存、长期分享与直链解析。"""

from typing import Any, Dict, List, Optional, Tuple

from app.runtime.log import logger

try:
    from p115client import P115Client
except ImportError:  # pragma: no cover - 依赖缺失时由插件给出提示
    P115Client = None  # type: ignore[assignment]


QRCODE_STATUS_MAP = {
    0: "waiting",
    1: "scanned",
    2: "confirmed",
}


class P115Error(RuntimeError):
    """115 相关操作的业务异常。"""


def _wrap_error(error: Exception, message: str) -> P115Error:
    """把底层异常包装成业务异常；业务异常原样透传，避免重复加前缀。"""
    if isinstance(error, P115Error):
        return error
    return P115Error(f"{message}：{error}")


class Pan115Client:
    """115 网盘客户端封装，统一错误处理与字段解析。"""

    def __init__(
        self,
        cookies: str = "",
        timeout: int = 60,
        proxy: Optional[str] = None,
    ) -> None:
        """保存登录凭据与请求参数，登录态按需惰性建立。"""
        self._cookies = str(cookies or "").strip()
        self._timeout = int(timeout or 60)
        self._proxy = proxy
        self._client: Optional[Any] = None

    @staticmethod
    def _ensure_dependency() -> None:
        """确认 p115client 依赖可用。"""
        if P115Client is None:
            raise P115Error("缺少依赖 p115client，请重新安装插件以完成依赖安装")

    def _request_kwargs(self) -> Dict[str, Any]:
        """构造统一的请求参数。"""
        return {"timeout": float(self._timeout)}

    def update_session(self, cookies: str) -> None:
        """更新登录 Cookie 并重建客户端。"""
        self._cookies = str(cookies or "").strip()
        self._client = None

    @property
    def cookies(self) -> str:
        """返回当前登录 Cookie。"""
        return self._cookies

    @property
    def is_authorized(self) -> bool:
        """判断当前是否已具备登录 Cookie。"""
        return bool(self._cookies)

    @property
    def client(self) -> Any:
        """返回 115 客户端实例，未登录时抛出业务异常。"""
        self._ensure_dependency()
        if not self._cookies:
            raise P115Error("115 未授权，请先扫码登录或填写 Cookie")
        if self._client is None:
            try:
                self._client = P115Client(self._cookies)
            except Exception as error:  # noqa: BLE001 - 统一转成业务异常
                raise _wrap_error(error, "初始化 115 客户端失败") from error
        return self._client

    def reset_client(self) -> None:
        """丢弃已缓存的客户端实例，便于重新登录。"""
        self._client = None

    @staticmethod
    def _data(resp: Any) -> Any:
        """从 115 响应中取出 data 字段。"""
        if isinstance(resp, dict):
            return resp.get("data")
        return None

    @staticmethod
    def _ok(resp: Any) -> bool:
        """判断 115 响应是否成功。"""
        if not isinstance(resp, dict):
            return bool(resp)
        return resp.get("state") is not False

    def check_login(self) -> Tuple[bool, str]:
        """校验当前 Cookie 是否有效，返回是否有效与账号信息。"""
        try:
            info = self.client.user_info()
        except Exception as error:  # noqa: BLE001
            return False, str(error)
        if not self._ok(info):
            message = ""
            if isinstance(info, dict):
                message = str(info.get("error") or info.get("msg") or "")
            return False, message or "Cookie 已失效"
        data = self._data(info) or {}
        account = ""
        if isinstance(data, dict):
            account = str(
                data.get("user_name")
                or data.get("uname")
                or data.get("user_id")
                or data.get("uid")
                or ""
            )
        return True, account

    def qrcode_token(self, app: str = "alipaymini") -> Dict[str, Any]:
        """申请扫码登录二维码令牌，默认使用与 115 App 匹配的客户端类型。"""
        self._ensure_dependency()
        try:
            resp = P115Client.login_qrcode_token(app=app, **self._request_kwargs())
        except Exception as error:  # noqa: BLE001
            raise _wrap_error(error, "获取二维码失败") from error
        data = self._data(resp) or {}
        if not isinstance(data, dict) or not data.get("uid"):
            raise P115Error(f"二维码响应异常：{resp}")
        return {
            "uid": data.get("uid"),
            "time": data.get("time"),
            "sign": data.get("sign"),
            "qrcode": data.get("qrcode"),
            "app": app,
        }

    def qrcode_status(
        self, uid: str, time_value: Any, sign: str, app: str = "alipaymini"
    ) -> Dict[str, Any]:
        """查询扫码状态，确认后换取 Cookie。"""
        self._ensure_dependency()
        payload = {"uid": uid, "time": time_value, "sign": sign}
        try:
            resp = P115Client.login_qrcode_scan_status(
                payload, **self._request_kwargs()
            )
        except Exception as error:  # noqa: BLE001
            return {"status": "error", "message": str(error)}
        data = self._data(resp) or {}
        status_code = data.get("status") if isinstance(data, dict) else None
        state = QRCODE_STATUS_MAP.get(status_code)
        if state is None:
            if status_code in (-1, -2):
                return {"status": "expired", "message": "二维码已失效，请刷新"}
            message = ""
            if isinstance(data, dict):
                message = str(data.get("msg") or "")
            return {"status": "waiting", "message": message}
        if state == "confirmed":
            cookie = self._fetch_cookie(uid=uid, app=app)
            if not cookie:
                return {"status": "error", "message": "登录成功但未获取到 Cookie"}
            self._cookies = cookie
            self._client = None
            return {"status": "confirmed", "message": "登录成功", "cookies": cookie}
        message = ""
        if isinstance(data, dict):
            message = str(data.get("msg") or "")
        return {"status": state, "message": message}

    def _fetch_cookie(self, uid: str, app: str = "alipaymini") -> str:
        """用已确认的登录令牌换取 Cookie 字符串。"""
        self._ensure_dependency()
        try:
            resp = P115Client.login_qrcode_scan_result(
                uid, app=app, **self._request_kwargs()
            )
        except Exception as error:  # noqa: BLE001 - 返回空表示失败
            logger.error(f"115 扫码换取 Cookie 失败：{error}")
            return ""
        cookie = (self._data(resp) or {})
        cookie = cookie.get("cookie") if isinstance(cookie, dict) else None
        if isinstance(cookie, dict):
            return "; ".join(f"{key}={value}" for key, value in cookie.items())
        return str(cookie or "")

    def ensure_folder(self, path: str) -> int:
        """按路径逐级创建目录并返回最终目录 id。"""
        target = str(path or "/").strip().strip("/")
        if not target:
            return 0
        pid = 0
        current = ""
        for name in [item for item in target.split("/") if item]:
            current = f"{current}/{name}"
            folder_id = self._dir_id_by_name(name, pid)
            if folder_id <= 0:
                try:
                    created = self.client.fs_mkdir(name, pid, **self._request_kwargs())
                except Exception as error:  # noqa: BLE001
                    raise _wrap_error(error, f"创建目录 {name} 失败") from error
                if not self._ok(created):
                    raise P115Error(f"创建目录 {name} 被拒绝：{created}")
                folder_id = int((self._data(created) or {}).get("cid") or 0)
            if folder_id <= 0:
                raise P115Error(f"无法定位或创建目录：{current}")
            pid = folder_id
        return pid

    def _dir_id_by_name(self, name: str, pid: int) -> int:
        """在指定目录下按名称查找子目录 id，不存在时返回 0。"""
        try:
            for item in self.list_folder(pid):
                if str(item.get("name") or "").strip() != name:
                    continue
                if item.get("is_dir"):
                    return int(item.get("fid") or 0)
        except P115Error as error:
            logger.debug(f"按名称查找目录失败：{error}")
        return 0

    def list_folder(self, cid: int = 0, limit: int = 1000) -> List[Dict[str, Any]]:
        """列出网盘目录下的条目，统一字段并自动翻页。"""
        entries: List[Dict[str, Any]] = []
        offset = 0
        while True:
            try:
                resp = self.client.fs_files(
                    {
                        "cid": int(cid),
                        "limit": limit,
                        "offset": offset,
                        "show_dir": 1,
                    },
                    **self._request_kwargs(),
                )
            except Exception as error:  # noqa: BLE001
                raise _wrap_error(error, "读取网盘目录失败") from error
            if not self._ok(resp):
                raise P115Error(f"读取网盘目录被拒绝：{resp}")
            data = self._data(resp)
            rows = data if isinstance(data, list) else (data or {}).get("list") or []
            normalized = self._normalize(rows)
            entries.extend(normalized)
            offset += len(rows)
            if len(rows) < limit:
                break
        return entries

    def list_share(
        self, share_code: str, receive_code: str = "", cid: int = 0
    ) -> List[Dict[str, Any]]:
        """列出分享链接中某一层的条目，统一字段并自动翻页取全。"""
        entries: List[Dict[str, Any]] = []
        offset = 0
        page_size = 1000
        while True:
            try:
                resp = self.client.share_snap(
                    {
                        "share_code": share_code,
                        "receive_code": receive_code or "",
                        "cid": int(cid),
                        "limit": page_size,
                        "offset": offset,
                    },
                    **self._request_kwargs(),
                )
            except Exception as error:  # noqa: BLE001
                raise _wrap_error(error, "读取分享内容失败") from error
            if not self._ok(resp):
                raise P115Error(f"读取分享内容被拒绝：{resp}")
            data = self._data(resp) or {}
            rows = list(data.get("list") or [])
            entries.extend(self._normalize(rows))
            offset += len(rows)
            count = int(data.get("count") or 0)
            if not rows or len(rows) < page_size or (count and offset >= count):
                break
        return entries

    @staticmethod
    def _normalize(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """把 115 原始条目转换为统一字段，屏蔽不同接口的命名差异。"""
        try:
            from p115client.tool.attr import normalize_attr
        except ImportError:  # pragma: no cover - 依赖缺失时使用原始字段
            normalize_attr = None  # type: ignore[assignment]
        result: List[Dict[str, Any]] = []
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            item: Dict[str, Any] = dict(row)
            if normalize_attr is not None:
                try:
                    normalized = normalize_attr(row)
                    item.update(
                        {
                            "fid": str(normalized.get("id") or ""),
                            "name": str(normalized.get("name") or ""),
                            "is_dir": bool(normalized.get("is_dir")),
                            "size": int(normalized.get("size") or 0),
                            "pickcode": str(normalized.get("pickcode") or ""),
                        }
                    )
                except Exception:  # noqa: BLE001 - 兜底使用原始字段
                    pass
            if not item.get("fid"):
                item["fid"] = str(item.get("fid") or item.get("id") or item.get("cid") or "")
            if not item.get("name"):
                item["name"] = str(item.get("n") or "")
            if "is_dir" not in item or item.get("is_dir") is None:
                item["is_dir"] = bool(item.get("cid") and not item.get("fid"))
            if not item.get("size"):
                item["size"] = int(item.get("s") or 0)
            result.append(item)
        return result

    def share_entries(
        self, share_code: str, receive_code: str = "", cid: int = 0
    ) -> Dict[str, Any]:
        """返回分享某一层的目录视图，包含条目与本层容量。"""
        entries = self.list_share(share_code, receive_code, cid)
        return {
            "cid": int(cid),
            "receive_code": receive_code or "",
            "entries": entries,
            "total_size": sum(int(item.get("size") or 0) for item in entries),
        }

    def share_info(self, share_code: str, receive_code: str = "") -> Dict[str, Any]:
        """读取分享的概要信息，例如标题、数量与容量。"""
        try:
            resp = self.client.share_snap(
                {
                    "share_code": share_code,
                    "receive_code": receive_code or "",
                    "cid": 0,
                    "limit": 1000,
                    "offset": 0,
                },
                **self._request_kwargs(),
            )
        except Exception as error:  # noqa: BLE001
            raise _wrap_error(error, "读取分享信息失败") from error
        if not self._ok(resp):
            raise P115Error(f"读取分享信息被拒绝：{resp}")
        data = self._data(resp) or {}
        rows = self._normalize(list(data.get("list") or []))
        info = data.get("shareinfo") or {}
        total_size = sum(int(item.get("size") or 0) for item in rows)
        return {
            "title": str(info.get("share_title") or "").strip(),
            "count": int(data.get("count") or len(rows)),
            "size": int(info.get("file_size") or total_size or 0),
            "receive_code": receive_code or "",
            "entries": rows,
        }

    def iter_share_media(
        self,
        share_code: str,
        receive_code: str = "",
        extensions: Optional[List[str]] = None,
        max_depth: int = 3,
    ) -> List[Dict[str, Any]]:
        """递归列出分享中的媒体文件，返回文件 id、相对目录与名称。"""
        wanted = {
            str(item).strip().lower().lstrip(".")
            for item in (extensions or [])
            if str(item).strip()
        }
        results: List[Dict[str, Any]] = []
        queue: List[tuple] = [(0, "", 0)]
        while queue:
            cid, prefix, depth = queue.pop(0)
            if depth > max_depth:
                continue
            for entry in self.list_share(share_code, receive_code, cid):
                name = str(entry.get("name") or "").strip()
                file_id = str(entry.get("fid") or "")
                if not name or not file_id:
                    continue
                if entry.get("is_dir"):
                    queue.append(
                        (int(file_id), f"{prefix}/{name}".strip("/"), depth + 1)
                    )
                    continue
                suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
                if wanted and suffix not in wanted:
                    continue
                results.append(
                    {
                        "fid": file_id,
                        "name": name,
                        "dir": prefix,
                        "size": int(entry.get("size") or 0),
                    }
                )
        return results

    def transfer(
        self,
        share_code: str,
        receive_code: str,
        file_ids: List[str],
        cid: int,
    ) -> Dict[str, Any]:
        """把分享中的文件转存到指定目录。"""
        payload = {
            "share_code": share_code,
            "receive_code": receive_code or "",
            "file_id": ",".join(str(item) for item in file_ids),
            "cid": int(cid),
            "is_check": 0,
        }
        try:
            resp = self.client.share_receive(payload, **self._request_kwargs())
        except Exception as error:  # noqa: BLE001
            raise _wrap_error(error, "转存失败") from error
        if not self._ok(resp):
            raise P115Error(f"转存被拒绝：{(resp or {}).get('error')}")
        return resp or {}

    def create_share(
        self, file_ids: List[str], duration: int = -1, auto_renewal: bool = True
    ) -> Dict[str, Any]:
        """为文件创建分享，并把有效期设置为长期。"""
        if not file_ids:
            raise P115Error("没有可分享的文件")
        try:
            resp = self.client.share_send(
                {
                    "file_ids": ",".join(str(item) for item in file_ids),
                    "ignore_warn": 1,
                },
                **self._request_kwargs(),
            )
        except Exception as error:  # noqa: BLE001
            raise _wrap_error(error, "创建分享失败") from error
        share_code = str((resp or {}).get("share_code") or "").strip()
        if not share_code:
            raise P115Error(f"创建分享返回异常：{resp}")
        receive_code = str((resp or {}).get("receive_code") or "").strip()
        self.update_share(
            share_code=share_code,
            receive_code=receive_code,
            duration=duration,
            auto_renewal=auto_renewal,
        )
        return {"share_code": share_code, "receive_code": receive_code}

    def update_share(
        self,
        share_code: str,
        receive_code: str = "",
        duration: int = -1,
        auto_renewal: bool = True,
    ) -> Dict[str, Any]:
        """修改分享配置，duration 为 -1 时表示长期有效。"""
        payload: Dict[str, Any] = {
            "share_code": share_code,
            "receive_code": receive_code or "",
            "share_duration": int(duration),
            "auto_renewal": 1 if auto_renewal else 0,
        }
        try:
            resp = self.client.share_update(payload, **self._request_kwargs())
        except Exception as error:  # noqa: BLE001
            raise _wrap_error(error, "设置分享有效期失败") from error
        if not self._ok(resp):
            raise P115Error(f"设置分享有效期被拒绝：{(resp or {}).get('error')}")
        return resp or {}

    def share_download_url(
        self, share_code: str, receive_code: str, file_id: str
    ) -> str:
        """解析分享中某个文件的直链下载地址。"""
        try:
            result = self.client.share_download_url(
                {
                    "share_code": share_code,
                    "receive_code": receive_code or "",
                    "file_id": str(file_id),
                },
                **self._request_kwargs(),
            )
        except Exception as error:  # noqa: BLE001
            raise _wrap_error(error, "解析分享直链失败") from error
        url = str(result or "").strip()
        if not url:
            raise P115Error("分享直链解析结果为空，请检查分享是否仍然有效")
        return url

    def build_share_link(self, share_code: str, receive_code: str = "") -> str:
        """拼接 115 分享访问链接。"""
        link = f"https://115.com/s/{share_code}"
        if receive_code:
            link = f"{link}?password={receive_code}"
        return link

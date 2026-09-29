"""Telegram 渠道：用户账号扫码授权后搜索指定频道中的网盘分享。"""

import asyncio
import re
import threading
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.runtime.log import logger

from ..core.config import TelegramConfig
from .models import PanResourceItem

U115_LINK_PATTERN = re.compile(r"https?://(?:115\.com|anxia\.com|115cdn\.com)/s/[0-9a-zA-Z]+[^\s\"'<]*")
RECEIVE_CODE_PATTERN = re.compile(r"(?:密码|提取码|访问码|password|pwd|code)\s*[:：]?\s*([0-9a-zA-Z]{4,8})")


class TelegramLoopRunner:
    """为 Telethon 提供常驻事件循环，避免跨请求复用不同的事件循环。"""

    _instance: Optional["TelegramLoopRunner"] = None
    _instance_lock = threading.Lock()

    def __init__(self) -> None:
        """初始化占位的后台循环状态。"""
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    @classmethod
    def instance(cls) -> "TelegramLoopRunner":
        """返回全局唯一的执行器实例。"""
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def _ensure_loop(self) -> None:
        """确保后台事件循环已启动。"""
        if self._loop is not None and self._loop.is_running():
            return
        with self._lock:
            if self._loop is not None and self._loop.is_running():
                return
            loop = asyncio.new_event_loop()

            def _run() -> None:
                """在后台线程中运行事件循环。"""
                asyncio.set_event_loop(loop)
                loop.run_forever()

            thread = threading.Thread(target=_run, name="pansearchstrm-telegram", daemon=True)
            thread.start()
            self._loop = loop
            self._thread = thread

    def submit(self, coroutine: Any, timeout: int = 120) -> Any:
        """把协程提交到后台事件循环并同步等待结果。"""
        self._ensure_loop()
        assert self._loop is not None
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result(timeout)


def _parse_proxy(proxy: Optional[str]) -> Any:
    """把 HTTP 代理地址转换为 Telethon 需要的元组。"""
    text = str(proxy or "").strip()
    if not text:
        return None
    try:
        import socks  # type: ignore[import-untyped]
    except ImportError:  # pragma: no cover - 缺少依赖时退回直连
        logger.warning("缺少 PySocks 依赖，Telegram 渠道将尝试直连")
        return None
    parsed = urlparse(text if "://" in text else f"http://{text}")
    if not parsed.hostname or not parsed.port:
        return None
    proxy_type = socks.SOCKS5 if parsed.scheme.startswith("socks") else socks.HTTP
    return proxy_type, parsed.hostname, parsed.port


class TelegramSearcher:
    """Telegram 渠道搜索器，支持扫码授权与频道关键词搜索。"""

    _pending: Dict[str, Any] = {}
    _pending_lock = threading.Lock()

    def __init__(
        self,
        config: TelegramConfig,
        proxy: Optional[str] = None,
        session: str = "",
    ) -> None:
        """保存渠道配置、代理与已保存的登录会话。"""
        self._config = config
        self._proxy = proxy
        self._session = str(session or "").strip()
        self._runner = TelegramLoopRunner.instance()

    def _build_client(self, session: str = ""):
        """构造 Telethon 客户端。"""
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        api_id = str(self._config.api_id or "").strip()
        api_hash = str(self._config.api_hash or "").strip()
        if not api_id or not api_hash:
            raise RuntimeError("Telegram 渠道缺少 api_id/api_hash 配置")
        return TelegramClient(
            StringSession(session or ""),
            int(api_id),
            api_hash,
            proxy=_parse_proxy(self._proxy),
            connection_retries=2,
            timeout=self._config.timeout,
        )

    async def _qr_start(self) -> Dict[str, Any]:
        """申请扫码登录二维码。"""
        self._close_pending()
        client = self._build_client()
        await client.connect()
        qr_login = await client.qr_login()
        with self._pending_lock:
            self._pending["client"] = client
            self._pending["login"] = qr_login
        return {"url": qr_login.url}

    async def _qr_wait(self, password: str = "") -> Dict[str, Any]:
        """等待用户扫码并在成功后保存会话。"""
        with self._pending_lock:
            client = self._pending.get("client")
            qr_login = self._pending.get("login")
        if client is None or qr_login is None:
            return {"status": "error", "message": "尚未发起扫码登录"}
        try:
            await qr_login.wait(timeout=self._config.timeout)
        except Exception as error:  # noqa: BLE001
            name = type(error).__name__
            if "SessionPasswordNeeded" in name:
                if not password:
                    return {"status": "password_required", "message": "该账号已开启两步验证，请输入密码"}
                try:
                    await client.sign_in(password=password)
                except Exception as inner:  # noqa: BLE001
                    return {"status": "error", "message": f"两步验证失败：{inner}"}
            elif "Timeout" in name:
                return {"status": "waiting", "message": "等待扫码超时，请重新获取二维码"}
            else:
                self._close_pending()
                return {"status": "error", "message": f"扫码登录失败：{error}"}
        session = client.session.save()
        self._session = session
        self._close_pending()
        return {"status": "confirmed", "message": "登录成功", "session": session}

    def _close_pending(self) -> None:
        """关闭并清理处于扫码等待中的客户端。"""
        with self._pending_lock:
            client = self._pending.pop("client", None)
            self._pending.pop("login", None)
        if client is not None:
            try:
                self._runner.submit(client.disconnect(), timeout=15)
            except Exception:  # noqa: BLE001 - 关闭失败不影响后续流程
                pass

    async def _search_channels(self, keyword: str) -> List[PanResourceItem]:
        """按关键词搜索配置的频道消息。"""
        client = self._build_client(self._session)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            raise RuntimeError("Telegram 未授权，请先扫码登录")
        items: List[PanResourceItem] = []
        try:
            for channel in self._config.channels:
                name = str(channel or "").strip()
                if not name:
                    continue
                if len(items) >= self._config.result_limit:
                    break
                try:
                    messages = await client.get_messages(
                        name, search=keyword, limit=50
                    )
                except Exception as error:  # noqa: BLE001 - 单频道失败继续
                    logger.error(f"Telegram 搜索频道 {name} 失败：{error}")
                    continue
                for message in messages or []:
                    items.extend(self._parse_message(message, name))
        finally:
            await client.disconnect()
        return items

    @staticmethod
    def _parse_message(message: Any, channel: str) -> List[PanResourceItem]:
        """从单条 Telegram 消息中提取网盘分享链接。"""
        items: List[PanResourceItem] = []
        text = str(getattr(message, "message", "") or "")
        candidates = U115_LINK_PATTERN.findall(text)
        try:
            buttons = getattr(message, "buttons", None) or []
        except Exception:  # noqa: BLE001
            buttons = []
        for row in buttons:
            for button in row or []:
                url = getattr(button, "url", None)
                if url:
                    candidates.extend(U115_LINK_PATTERN.findall(str(url)))
        code_match = RECEIVE_CODE_PATTERN.search(text)
        access_code = code_match.group(1) if code_match else ""
        title = (text.strip().splitlines() or [""])[0][:120]
        for link in dict.fromkeys(candidates):
            items.append(
                PanResourceItem(
                    source="telegram",
                    title=title or link,
                    share_url=link,
                    access_code=access_code,
                    resource_type="115",
                    pubdate=str(getattr(message, "date", "") or ""),
                    channel=channel,
                )
            )
        return items

    def qr_start(self) -> Dict[str, Any]:
        """同步入口：申请扫码登录二维码。"""
        try:
            return self._runner.submit(self._qr_start(), timeout=self._config.timeout + 30)
        except Exception as error:  # noqa: BLE001
            return {"status": "error", "message": f"获取二维码失败：{error}"}

    def qr_wait(self, password: str = "") -> Dict[str, Any]:
        """同步入口：等待扫码结果。"""
        try:
            return self._runner.submit(self._qr_wait(password), timeout=self._config.timeout + 60)
        except Exception as error:  # noqa: BLE001
            return {"status": "error", "message": f"等待扫码失败：{error}"}

    def search(self, keyword: str) -> List[PanResourceItem]:
        """同步入口：搜索频道消息中的网盘分享。"""
        if not self._session:
            logger.warning("Telegram 未登录，跳过该渠道")
            return []
        try:
            items = self._runner.submit(
                self._search_channels(keyword), timeout=self._config.timeout + 60
            )
        except Exception as error:  # noqa: BLE001
            logger.error(f"Telegram 搜索失败：{error}")
            return []
        return items[: self._config.result_limit]

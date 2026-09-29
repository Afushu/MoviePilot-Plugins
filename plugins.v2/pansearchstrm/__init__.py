"""网盘搜索 STRM 插件：搜索网盘资源、115 转存与长期分享、生成 STRM。"""

from typing import Any, Dict, List, Optional, Tuple

from app.runtime.log import logger
from app.schemas.types import MediaType
from app.sdk.plugin.base import _PluginBase

from .api import PanSearchApi
from .core.config import PanSearchStrmConfig
from .core.p115 import Pan115Client
from .core.utils import get_proxy_url
from .helper.pipeline import TransferPipeline
from .search import PanSearchAggregator
from .search.models import PanResourceItem
from .search.telegram import TelegramSearcher


class PanSearchStrm(_PluginBase):
    """网盘搜索 STRM 插件入口。"""

    plugin_name = "网盘搜索STRM"
    plugin_desc = "搜索盘搜、聚影与 Telegram 的网盘资源，115 扫码授权后一键转存、生成长期分享并落地 STRM。"
    plugin_icon = "pansearchstrm.png"
    plugin_version = "1.0.0"
    plugin_label = "网盘"
    plugin_author = "Afushu"
    author_url = "https://github.com/Afushu"
    plugin_config_prefix = "pansearchstrm_"
    plugin_order = 22
    auth_level = 1

    _config: PanSearchStrmConfig = PanSearchStrmConfig()
    _enabled: bool = False
    _client: Optional[Pan115Client] = None
    _api: Optional[PanSearchApi] = None

    def init_plugin(self, config: Dict[str, Any] = None) -> None:
        """根据配置初始化插件运行状态。"""
        self.stop_service()
        self._config = PanSearchStrmConfig.from_dict(config)
        self._enabled = bool(self._config.enabled)
        self._client = None
        self._api = None
        if self._enabled:
            logger.info(
                "网盘搜索STRM 已启用，渠道：%s" % ",".join(self.aggregator().enabled_sources())
            )

    def get_state(self) -> bool:
        """返回插件启用状态。"""
        return bool(self._enabled)

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """返回插件远程命令列表。"""
        return [
            {
                "cmd": "/psearch",
                "event": "PluginAction",
                "desc": "搜索网盘资源",
                "category": "网盘",
                "data": {"action": "psearch"},
            }
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        """返回插件 HTTP 接口列表。"""
        api = self._api_instance()
        return [
            {
                "path": "/status",
                "endpoint": api.status,
                "methods": ["GET"],
                "summary": "插件与账号状态",
                "auth": "bear",
            },
            {
                "path": "/config",
                "endpoint": api.get_config,
                "methods": ["GET"],
                "summary": "读取插件配置",
                "auth": "bear",
            },
            {
                "path": "/config",
                "endpoint": api.save_config,
                "methods": ["POST"],
                "summary": "保存插件配置",
                "auth": "bear",
            },
            {
                "path": "/qrcode/115",
                "endpoint": api.qrcode_115,
                "methods": ["GET"],
                "summary": "获取 115 扫码登录二维码",
                "auth": "bear",
            },
            {
                "path": "/qrcode/115/status",
                "endpoint": api.qrcode_115_status,
                "methods": ["GET"],
                "summary": "轮询 115 扫码状态",
                "auth": "bear",
            },
            {
                "path": "/browse",
                "endpoint": api.browse_115,
                "methods": ["GET"],
                "summary": "浏览 115 网盘目录",
                "auth": "bear",
            },
            {
                "path": "/qrcode/telegram",
                "endpoint": api.qrcode_telegram,
                "methods": ["GET"],
                "summary": "获取 Telegram 扫码登录二维码",
                "auth": "bear",
            },
            {
                "path": "/qrcode/telegram/wait",
                "endpoint": api.telegram_wait,
                "methods": ["POST"],
                "summary": "等待 Telegram 扫码结果",
                "auth": "bear",
            },
            {
                "path": "/search",
                "endpoint": api.search,
                "methods": ["POST"],
                "summary": "搜索网盘资源",
                "auth": "bear",
            },
            {
                "path": "/transfer",
                "endpoint": api.transfer,
                "methods": ["POST"],
                "summary": "转存并生成 STRM",
                "auth": "bear",
            },
            {
                "path": "/records",
                "endpoint": api.records,
                "methods": ["GET"],
                "summary": "转存记录",
                "auth": "bear",
            },
            {
                "path": "/records/remove",
                "endpoint": api.remove_record,
                "methods": ["POST"],
                "summary": "移除转存记录",
                "auth": "bear",
            },
            {
                "path": "/p115/cookie",
                "endpoint": api.get_cookie,
                "methods": ["GET"],
                "summary": "读取 115 登录状态",
                "auth": "bear",
            },
            {
                "path": "/p115/cookie",
                "endpoint": api.set_cookie,
                "methods": ["POST"],
                "summary": "手动设置 115 Cookie",
                "auth": "bear",
            },
            {
                "path": "/link/preview",
                "endpoint": api.link_preview,
                "methods": ["POST"],
                "summary": "解析 115 分享链接",
                "auth": "bear",
            },
            {
                "path": "/link/browse",
                "endpoint": api.link_browse,
                "methods": ["POST"],
                "summary": "浏览分享目录",
                "auth": "bear",
            },
            {
                "path": "/link/transfer",
                "endpoint": api.link_transfer,
                "methods": ["POST"],
                "summary": "转存分享内容",
                "auth": "bear",
            },
            {
                "path": "/link/strm",
                "endpoint": api.link_strm,
                "methods": ["POST"],
                "summary": "转存并生成 STRM",
                "auth": "bear",
            },
            {
                "path": "/redirect",
                "endpoint": api.redirect,
                "methods": ["GET"],
                "summary": "分享直链跳转",
                "allow_anonymous": True,
            },
        ]

    def get_module(self) -> Dict[str, Any]:
        """把网盘资源源注册到 MoviePilot 搜索链。"""
        return {
            "search_torrents": self.search_torrents,
            "async_search_torrents": self.async_search_torrents,
        }

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """声明插件使用 Vue 联邦组件渲染。"""
        return "vue", "dist/assets"

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """Vue 模式下返回默认配置模型。"""
        return [], self._config.model_dump()

    def get_page(self) -> Optional[List[dict]]:
        """Vue 模式下详情页由远程组件渲染。"""
        return []

    def get_sidebar_nav(self) -> List[Dict[str, Any]]:
        """声明主界面侧栏入口。"""
        if not self.get_state():
            return []
        return [
            {
                "nav_key": "main",
                "title": "网盘搜索",
                "icon": "mdi-cloud-search",
                "section": "discovery",
                "permission": "discover",
                "order": 30,
            }
        ]

    def stop_service(self) -> None:
        """停止插件后台服务并释放资源。"""
        return None

    def _api_instance(self) -> PanSearchApi:
        """返回插件接口实例。"""
        if self._api is None:
            self._api = PanSearchApi(self)
        return self._api

    def get_config_model(self) -> PanSearchStrmConfig:
        """返回当前配置模型。"""
        return self._config

    def save_config_model(self, payload: Dict[str, Any]) -> PanSearchStrmConfig:
        """保存配置并立即生效。"""
        config = PanSearchStrmConfig.from_dict(payload)
        self.update_config(config.model_dump())
        self.init_plugin(config.model_dump())
        return config

    def get_115_client(self) -> Pan115Client:
        """返回 115 客户端单例。"""
        if self._client is None:
            self._client = Pan115Client(
                cookies=self.get_data("p115_cookies") or self._config.p115.cookies,
                timeout=self._config.p115.request_timeout,
                proxy=get_proxy_url(),
            )
        return self._client

    def persist_115_cookies(self, cookies: str) -> None:
        """持久化 115 登录 Cookie 并通知用户。"""
        self.save_data("p115_cookies", cookies)
        self._config.p115.cookies = cookies
        client = self.get_115_client()
        client.update_session(cookies)
        self.update_config(self._config.model_dump())
        if self._config.notify:
            self.post_message(
                mtype="网盘搜索STRM",
                title="【网盘搜索STRM】115 授权成功",
                text="115 网盘已完成扫码授权。",
            )

    def get_115_pending(self) -> Dict[str, Any]:
        """读取待完成的 115 扫码会话。"""
        return self.get_data("p115_pending") or {}

    def save_115_pending(self, token: Dict[str, Any]) -> None:
        """保存待完成的 115 扫码会话。"""
        self.save_data("p115_pending", token or {})

    def clear_115_pending(self) -> None:
        """清理 115 扫码会话。"""
        self.del_data("p115_pending")

    def get_telegram_session(self) -> str:
        """读取 Telegram 登录会话。"""
        return str(self.get_data("telegram_session") or "")

    def persist_telegram_session(self, session: str) -> None:
        """保存 Telegram 登录会话并通知用户。"""
        self.save_data("telegram_session", session)
        if self._config.notify:
            self.post_message(
                mtype="网盘搜索STRM",
                title="【网盘搜索STRM】Telegram 授权成功",
                text="Telegram 渠道已可正常搜索。",
            )

    def build_telegram_searcher(self) -> TelegramSearcher:
        """构造 Telegram 渠道搜索器。"""
        return TelegramSearcher(
            config=self._config.telegram,
            proxy=get_proxy_url(),
            session=self.get_telegram_session(),
        )

    def aggregator(self) -> PanSearchAggregator:
        """构造搜索聚合器。"""
        return PanSearchAggregator(self._config)

    def transfer_pipeline(self) -> TransferPipeline:
        """构造转存流水线。"""
        return TransferPipeline(self._config, self.get_115_client())

    def remember_record(self, record: Dict[str, Any]) -> None:
        """记录一次转存或 STRM 操作，并发送通知。"""
        records = list(self.get_data("records") or [])
        records.insert(0, record)
        self.save_data("records", records[:200])
        if not self._config.notify:
            return
        result = record.get("result") or {}
        self.post_message(
            mtype="网盘搜索STRM",
            title="【网盘搜索STRM】操作完成",
            text=(
                f"{record.get('title') or ''}\n"
                f"生成 STRM：{result.get('total', 0)} 个\n"
                f"输出目录：{result.get('output_path', '')}"
            ),
        )

    def search_media(self, keyword: str) -> List[PanResourceItem]:
        """按关键词搜索网盘资源，供插件与命令复用。"""
        return self.aggregator().search(keyword)

    def transfer_item(self, item: PanResourceItem, sub_path: str = "") -> Dict[str, Any]:
        """执行转存、长期分享与 STRM 生成，并记录结果。"""
        result = self.transfer_pipeline().run(item=item, sub_path=sub_path)
        self.remember_record(
            {
                "source": item.source,
                "title": item.title,
                "share_url": item.share_url,
                "result": result,
            }
        )
        return result

    def search_torrents(
        self,
        site: dict = None,
        keyword: str = "",
        mtype: Optional[MediaType] = None,
        page: Optional[int] = 0,
    ) -> List[Any]:
        """同步搜索网盘资源，并把结果注入 MoviePilot 搜索链。"""
        if not self.get_state() or not keyword:
            return []
        if not self._config.search_inject_enabled:
            return []
        channels = self.aggregator().enabled_sources()
        items = self.aggregator().search(keyword)
        logger.info(
            f"网盘资源源参与搜索：keyword={keyword}，渠道={channels or '未启用'}，返回 {len(items)} 条"
        )
        return [self.aggregator().to_torrent_info(item) for item in items]

    async def async_search_torrents(
        self,
        site: dict = None,
        keyword: str = "",
        mtype: Optional[MediaType] = None,
        page: Optional[int] = 0,
    ) -> List[Any]:
        """异步搜索网盘资源，把耗时渠道放到线程池执行。"""
        import asyncio

        return await asyncio.to_thread(
            self.search_torrents, site, keyword, mtype, page
        )

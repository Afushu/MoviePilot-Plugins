"""网盘资源搜索渠道的聚合入口。"""

from typing import Any, Dict, List

from app.runtime.log import logger

from ..core.config import PanSearchStrmConfig
from ..core.utils import clean_keyword, get_proxy_url
from .models import PanResourceItem
from .juying import JuyingSearcher
from .pansou import PanSouSearcher
from .telegram import TelegramSearcher


class PanSearchAggregator:
    """并行聚合盘搜、聚影与 Telegram 三个渠道的搜索结果。"""

    def __init__(self, config: PanSearchStrmConfig) -> None:
        """按配置初始化各渠道搜索器。"""
        self._config = config
        self._proxy = get_proxy_url()

    def search(self, keyword: str, sources: List[str] = None) -> List[PanResourceItem]:
        """按指定渠道搜索网盘资源，未指定时使用全部已启用渠道。"""
        query = clean_keyword(keyword)
        if not query:
            return []
        enabled = sources or self.enabled_sources()
        results: List[PanResourceItem] = []
        for name in enabled:
            try:
                results.extend(self._search_one(name, query))
            except Exception as error:  # noqa: BLE001 - 单渠道失败不影响整体
                logger.error(f"网盘搜索渠道 {name} 失败：{error}")
        return results

    def enabled_sources(self) -> List[str]:
        """返回当前已启用的渠道名称列表。"""
        names: List[str] = []
        if self._config.pansou.enabled:
            names.append("pansou")
        if self._config.juying.enabled:
            names.append("juying")
        if self._config.telegram.enabled:
            names.append("telegram")
        return names

    def _search_one(self, name: str, keyword: str) -> List[PanResourceItem]:
        """调用单个渠道执行搜索。"""
        if name == "pansou":
            return PanSouSearcher(self._config.pansou, self._proxy).search(keyword)
        if name == "juying":
            return JuyingSearcher(self._config.juying, self._proxy).search(keyword)
        if name == "telegram":
            return TelegramSearcher(self._config.telegram, self._proxy).search(keyword)
        logger.warning(f"未知的网盘搜索渠道：{name}")
        return []

    @staticmethod
    def to_torrent_info(item: PanResourceItem, media: Any = None) -> Any:
        """把网盘资源转换为 MoviePilot 的种子信息，便于注入搜索结果。"""
        from app.domain.context import TorrentInfo

        torrent = TorrentInfo(
            site=0,
            site_name=f"网盘·{item.source}",
            title=item.display_title,
            description=item.description,
            enclosure=item.share_url,
            page_url=item.share_url,
            size=item.size_bytes,
            pubdate=item.pubdate,
            labels=["网盘资源", item.resource_type.upper() or "115"],
            category=getattr(media, "category", None),
        )
        if media is not None:
            torrent.media_source = getattr(media, "media_source", None)
            torrent.media_id = getattr(media, "media_id", None)
        return torrent

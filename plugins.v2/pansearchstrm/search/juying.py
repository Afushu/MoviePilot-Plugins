"""聚影（Juying）渠道：登录站点后按影片搜索其网盘资源。"""

import re
from typing import Any, Dict, List, Optional

import httpx

from app.runtime.log import logger

from ..core.config import JuyingConfig
from ..core.utils import build_proxies
from .models import PanResourceItem


class JuyingSearcher:
    """聚影渠道搜索器。"""

    def __init__(self, config: JuyingConfig, proxy: Optional[str] = None) -> None:
        """保存渠道配置与网络代理。"""
        self._config = config
        self._proxy = proxy
        self._csrf = ""
        self._logged_in = False

    def _client(self) -> httpx.Client:
        """构造带超时与代理的 HTTP 客户端。"""
        return httpx.Client(
            timeout=self._config.timeout,
            proxies=build_proxies(self._proxy),
            follow_redirects=True,
            headers={"User-Agent": "MoviePilot-PanSearch/1.0"},
        )

    def _login(self, client: httpx.Client) -> bool:
        """登录聚影站点并记录 CSRF 令牌。"""
        if self._logged_in:
            return True
        base = self._config.base_url.rstrip("/")
        if not self._config.username:
            logger.warning("聚影渠道未配置账号，跳过登录")
            return False
        try:
            client.get(f"{base}/api/csrf/")
            self._csrf = client.cookies.get("csrftoken") or ""
            headers = {"X-CSRFToken": self._csrf, "Referer": f"{base}/"}
            response = client.post(
                f"{base}/api/app/login/",
                headers=headers,
                json={
                    "username": self._config.username,
                    "password": self._config.password,
                },
            )
            payload = response.json()
        except Exception as error:  # noqa: BLE001
            logger.error(f"聚影登录失败：{error}")
            return False
        if isinstance(payload, dict) and payload.get("success") is False:
            logger.error(f"聚影登录被拒绝：{payload.get('message')}")
            return False
        self._logged_in = True
        return True

    def search(self, keyword: str) -> List[PanResourceItem]:
        """按影片名搜索聚影资源。"""
        base = self._config.base_url.rstrip("/")
        if not base:
            return []
        items: List[PanResourceItem] = []
        with self._client() as client:
            if not self._login(client):
                return []
            try:
                response = client.get(
                    f"{base}/api/app/movies/",
                    params={"q": keyword, "page": 1, "page_size": 30},
                )
                payload = response.json()
            except Exception as error:  # noqa: BLE001
                logger.error(f"聚影影片搜索失败：{error}")
                return []
            movies = payload.get("results") if isinstance(payload, dict) else []
            for movie in movies or []:
                if len(items) >= self._config.result_limit:
                    break
                if not isinstance(movie, dict):
                    continue
                movie_id = movie.get("id")
                if not movie_id:
                    continue
                items.extend(self._load_resources(client, base, movie_id, movie))
        return items[: self._config.result_limit]

    def _load_resources(
        self,
        client: httpx.Client,
        base: str,
        movie_id: Any,
        movie: Dict[str, Any],
    ) -> List[PanResourceItem]:
        """读取单个影片下的资源条目。"""
        movie_title = str(movie.get("title") or movie.get("name") or "").strip()
        year = str(movie.get("year") or "").strip()
        try:
            response = client.get(
                f"{base}/api/app/movie/{movie_id}/resources/",
                params={"page": 1, "page_size": 120},
            )
            payload = response.json()
        except Exception as error:  # noqa: BLE001
            logger.error(f"聚影读取资源失败（影片 {movie_id}）：{error}")
            return []
        items: List[PanResourceItem] = []
        for row in (payload.get("resources") if isinstance(payload, dict) else []) or []:
            if not isinstance(row, dict):
                continue
            resource_id = str(row.get("id") or "").strip()
            share_url = str(
                row.get("share_link")
                or row.get("raw_share_link")
                or row.get("share_link_with_code")
                or ""
            ).strip()
            if not resource_id:
                continue
            items.append(
                PanResourceItem(
                    source="juying",
                    title=str(
                        row.get("title") or row.get("resource_description") or movie_title
                    ).strip(),
                    share_url=share_url,
                    access_code=str(row.get("access_code") or "").strip(),
                    resource_type=str(row.get("resource_type") or "").strip().lower(),
                    size_text=self._size_text(row.get("resource_size")),
                    pubdate=str(row.get("created_at") or row.get("updated_at") or "").strip(),
                    channel=f"{movie_title} {year}".strip(),
                    extra={
                        "resource_id": resource_id,
                        "access_ticket": str(row.get("access_ticket") or "").strip(),
                        "link_exposed": bool(row.get("link_exposed")),
                        "movie_id": str(movie_id),
                    },
                )
            )
        return items

    def resolve(self, item: PanResourceItem) -> PanResourceItem:
        """解析聚影资源票据，补齐真实分享链接与提取码。"""
        resource_id = str(item.extra.get("resource_id") or "").strip()
        ticket = str(item.extra.get("access_ticket") or "").strip()
        if not resource_id or not ticket:
            return item
        base = self._config.base_url.rstrip("/")
        with self._client() as client:
            if not self._login(client):
                return item
            try:
                response = client.post(
                    f"{base}/api/app/resource/{resource_id}/access/",
                    headers={"X-CSRFToken": self._csrf, "Referer": f"{base}/"},
                    json={"access_ticket": ticket},
                )
                payload = response.json()
            except Exception as error:  # noqa: BLE001
                logger.error(f"聚影解析资源失败：{error}")
                return item
        if not isinstance(payload, dict):
            return item
        target = str(payload.get("target") or "").strip()
        code = str(payload.get("access_code") or "").strip()
        if target:
            item.share_url = self._with_code(target, code)
        if code:
            item.access_code = code
        item.extra["access_mode"] = str(payload.get("access_mode") or "")
        return item

    @staticmethod
    def _with_code(target: str, code: str) -> str:
        """把提取码拼接到分享链接上。"""
        if not code or "password=" in target or "pwd=" in target:
            return target
        return f"{target}?password={code}"

    @staticmethod
    def _size_text(value: Any) -> str:
        """把聚影返回的资源大小转换为可读文本。"""
        text = str(value or "").strip()
        if not text:
            return ""
        return f"{text}GB" if re.fullmatch(r"\d+(?:\.\d+)?", text) else text

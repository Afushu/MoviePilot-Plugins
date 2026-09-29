"""盘搜（PanSou）渠道：通过其 HTTP API 搜索网盘分享资源。"""

from typing import Any, Dict, List, Optional

import httpx

from app.runtime.log import logger

from ..core.config import PanSouConfig
from ..core.utils import build_proxies
from .models import PanResourceItem

AUTH_SESSION_KEY = "pansou_auth"


class PanSouSearcher:
    """盘搜渠道搜索器。"""

    def __init__(self, config: PanSouConfig, proxy: Optional[str] = None) -> None:
        """保存渠道配置与网络代理。"""
        self._config = config
        self._proxy = proxy
        self._token = ""

    def _client(self) -> httpx.Client:
        """构造带超时与代理的 HTTP 客户端。"""
        return httpx.Client(
            timeout=self._config.timeout,
            proxies=build_proxies(self._proxy),
            follow_redirects=True,
            headers={"User-Agent": "MoviePilot-PanSearch/1.0"},
        )

    def _login(self, client: httpx.Client) -> str:
        """按需登录盘搜服务并返回访问令牌。"""
        if not self._config.username:
            return ""
        if self._token:
            return self._token
        url = f"{self._config.base_url.rstrip('/')}/api/auth/login"
        try:
            response = client.post(
                url,
                json={
                    "username": self._config.username,
                    "password": self._config.password,
                },
            )
            payload = response.json()
        except Exception as error:  # noqa: BLE001
            logger.error(f"盘搜登录失败：{error}")
            return ""
        data = payload.get("data") if isinstance(payload, dict) else None
        token = ""
        if isinstance(data, dict):
            token = str(data.get("token") or data.get("access_token") or "")
        if not token and isinstance(payload, dict):
            token = str(payload.get("token") or "")
        self._token = token
        return token

    def search(self, keyword: str) -> List[PanResourceItem]:
        """调用盘搜搜索接口并解析结果。"""
        base = self._config.base_url.rstrip("/")
        if not base:
            return []
        items: List[PanResourceItem] = []
        with self._client() as client:
            headers: Dict[str, str] = {"Content-Type": "application/json"}
            token = self._login(client)
            if self._config.username and not token:
                logger.warning("盘搜需要认证但未取得令牌，跳过该渠道")
                return []
            if token:
                headers["Authorization"] = f"Bearer {token}"
            try:
                response = client.post(
                    f"{base}/api/search",
                    headers=headers,
                    json={
                        "kw": keyword,
                        "refresh": False,
                        "res": "results",
                        "src": "all",
                    },
                )
                payload = response.json()
            except Exception as error:  # noqa: BLE001
                logger.error(f"盘搜搜索失败：{error}")
                return []
        items.extend(self._parse(payload))
        return items[: self._config.result_limit]

    @staticmethod
    def _parse(payload: Any) -> List[PanResourceItem]:
        """解析盘搜响应中的分享链接列表。"""
        items: List[PanResourceItem] = []
        if not isinstance(payload, dict):
            return items
        data = payload.get("data")
        if isinstance(data, dict):
            rows = data.get("results") or data.get("list") or []
        elif isinstance(data, list):
            rows = data
        else:
            rows = payload.get("results") or []
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            message = row.get("message") if isinstance(row.get("message"), dict) else {}
            title = str(
                message.get("title") or row.get("title") or row.get("name") or ""
            ).strip()
            channel = str(message.get("channel") or row.get("channel") or "").strip()
            pubdate = str(
                message.get("datetime") or row.get("datetime") or row.get("time") or ""
            ).strip()
            links = row.get("links") or []
            if isinstance(links, dict):
                links = [links]
            for link in links:
                if not isinstance(link, dict):
                    continue
                url = str(link.get("url") or "").strip()
                if not url:
                    continue
                link_type = str(link.get("type") or "").strip().lower()
                password = str(
                    link.get("password") or link.get("pwd") or link.get("code") or ""
                ).strip()
                items.append(
                    PanResourceItem(
                        source="pansou",
                        title=title or url,
                        share_url=url,
                        access_code=password,
                        resource_type=link_type,
                        size_text=str(row.get("size") or "").strip(),
                        pubdate=pubdate,
                        channel=channel,
                    )
                )
        return items

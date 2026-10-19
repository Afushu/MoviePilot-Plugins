"""网盘搜索结果的统一数据模型。"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class PanResourceItem:
    """一条统一的网盘资源搜索结果。"""

    source: str = ""
    title: str = ""
    share_url: str = ""
    access_code: str = ""
    resource_type: str = ""
    size_text: str = ""
    size_bytes: float = 0.0
    pubdate: str = ""
    channel: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_title(self) -> str:
        """返回用于展示的标题，附带提取码信息。"""
        parts = [f"[{self.source}]", self.title or self.share_url]
        if self.access_code:
            parts.append(f"提取码:{self.access_code}")
        if self.size_text:
            parts.append(f"大小:{self.size_text}")
        return " ".join(part for part in parts if part).strip()

    @property
    def description(self) -> str:
        """返回用于展示的副标题。"""
        pieces = [
            f"来源：{self.source}",
            f"网盘：{self.resource_type or '未知'}",
        ]
        if self.channel:
            pieces.append(f"频道：{self.channel}")
        if self.share_url:
            pieces.append(self.share_url)
        return " | ".join(pieces)

    def to_dict(self) -> Dict[str, Any]:
        """转换为可 JSON 序列化的字典。"""
        return {
            "source": self.source,
            "title": self.title,
            "share_url": self.share_url,
            "access_code": self.access_code,
            "resource_type": self.resource_type,
            "size_text": self.size_text,
            "size_bytes": self.size_bytes,
            "pubdate": self.pubdate,
            "channel": self.channel,
            "extra": self.extra,
        }

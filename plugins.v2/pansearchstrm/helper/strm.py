"""STRM 文件生成：把网盘条目写成可被媒体服务器识别的文本文件。"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from app.runtime.log import logger


def sanitize_name(name: str, fallback: str = "unnamed") -> str:
    """清洗文件或目录名中的非法字符。"""
    text = str(name or "").strip()
    text = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text or fallback


def is_media_file(name: str, extensions: List[str]) -> bool:
    """判断文件名是否为配置中的媒体类型。"""
    suffix = Path(str(name or "")).suffix.lower().lstrip(".")
    if not suffix:
        return False
    return suffix in {item.strip().lower() for item in extensions if item.strip()}


class StrmWriter:
    """负责按条目生成 STRM 文件。"""

    def __init__(
        self,
        output_path: str,
        redirect_base: str = "",
        url_mode: str = "redirect",
        overwrite: bool = False,
    ) -> None:
        """保存输出目录、跳转端点与覆盖策略。"""
        self._output_path = str(output_path or "").strip()
        self._redirect_base = str(redirect_base or "").rstrip("/")
        self._url_mode = str(url_mode or "redirect").strip().lower()
        self._overwrite = bool(overwrite)

    def build_url(
        self,
        share_code: str,
        receive_code: str,
        file_id: str,
        file_name: str = "",
        share_link: str = "",
    ) -> str:
        """按配置模式构造 STRM 中写入的地址。"""
        if self._url_mode == "share":
            return share_link or (
                f"https://115.com/s/{share_code}?password={receive_code}"
            )
        if not self._redirect_base:
            raise ValueError("未配置 MoviePilot 访问地址，无法生成跳转端点")
        query = (
            f"?share_code={quote(str(share_code))}"
            f"&receive_code={quote(str(receive_code or ''))}"
            f"&file_id={quote(str(file_id))}"
        )
        if file_name:
            query += f"&file_name={quote(str(file_name))}"
        return f"{self._redirect_base}/api/v1/plugin/PanSearchStrm/redirect{query}"

    def write(
        self,
        title: str,
        file_name: str,
        url: str,
        sub_path: str = "",
    ) -> Optional[str]:
        """写入单个 STRM 文件并返回其绝对路径。"""
        if not self._output_path:
            raise ValueError("未配置 STRM 输出目录")
        folder = Path(self._output_path)
        if sub_path:
            folder = folder / sanitize_name(sub_path)
        folder = folder / sanitize_name(title)
        folder.mkdir(parents=True, exist_ok=True)
        stem = Path(str(file_name or "video")).stem or "video"
        target = folder / f"{sanitize_name(stem)}.strm"
        if target.exists() and not self._overwrite:
            return str(target)
        target.write_text(url, encoding="utf-8")
        logger.info(f"已生成 STRM：{target}")
        return str(target)

    def summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """汇总生成结果，便于接口返回。"""
        return {
            "total": len(records),
            "output_path": self._output_path,
            "url_mode": self._url_mode,
            "files": records,
        }

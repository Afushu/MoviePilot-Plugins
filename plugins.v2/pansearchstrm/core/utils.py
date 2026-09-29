"""插件通用工具：代理读取、HTTP 客户端与关键字清洗。"""

import re
from typing import Any, Dict, Optional

from app.runtime.log import logger


def get_proxy_url() -> Optional[str]:
    """读取 MoviePilot 配置中的网络代理地址。"""
    try:
        from app.runtime.config import settings
    except Exception:  # noqa: BLE001 - 配置不可用时不影响无代理场景
        return None
    for name in ("PROXY_HOST", "PROXY"):
        value = getattr(settings, name, None)
        text = str(value or "").strip()
        if text:
            return text
    return None


def build_proxies(proxy: Optional[str]) -> Optional[Dict[str, str]]:
    """把代理地址转换为 requests 风格的 proxies 参数。"""
    text = str(proxy or "").strip()
    if not text:
        return None
    return {"http": text, "https": text}


def clean_keyword(keyword: str) -> str:
    """清洗搜索关键词，去掉多余空白与常见噪声字符。"""
    text = str(keyword or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_share_payload(url: str) -> Dict[str, str]:
    """从 115 分享链接中提取分享码与提取码。"""
    text = str(url or "").strip()
    result = {"share_code": "", "receive_code": ""}
    if not text:
        return result
    try:
        from p115client.util import share_extract_payload

        payload = share_extract_payload(text) or {}
        share_code = str(payload.get("share_code") or "").strip()
        receive_code = str(payload.get("receive_code") or "").strip()
        if share_code:
            return {"share_code": share_code, "receive_code": receive_code}
    except Exception:  # noqa: BLE001 - 退回正则解析
        pass
    matched = re.search(
        r"(?:115\.com|115cdn\.com|anxia\.com|115pan\.com)/s/([0-9a-zA-Z]+)", text
    )
    if matched:
        result["share_code"] = matched.group(1)
    code = re.search(r"(?:password|pwd|code)=([0-9a-zA-Z]{4,8})", text)
    if code:
        result["receive_code"] = code.group(1)
    return result


def log_debug(message: str) -> None:
    """输出插件调试日志，异常时静默忽略。"""
    try:
        logger.debug(message)
    except Exception:  # noqa: BLE001
        pass

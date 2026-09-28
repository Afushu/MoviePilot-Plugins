"""下载失败冷却调优插件。

在运行期对主程序的三处下载失败冷却行为做补丁修正：

1. 冷却时长可配置：主程序把资源级失败（下载链接失效、种子被删或被替换等）
   的冷却硬编码为 24 小时，长于站点资源池刷新周期，会让已经恢复可用的资源
   被长期静默跳过，甚至跨过站点免费期。插件改为从自身配置读取分钟数。
2. 冷却指纹纳入下载链接：站点每次抓取都会重新签发带签名的下载直链，
   主程序的失败指纹只看媒体、季集、站点与资源 id，不含链接，
   因此站点重新签发的有效链接也会被旧链接的失败记录拦住。
3. 失败原因如实落库：主程序在写冷却记录时把原因固定为「下载种子内容为空」，
   真实错误（例如「下载种子出错，状态码：404」）只出现在通知里。插件在取种
   环节记录真实原因，并在写入冷却记录时替换占位文案。
"""

import hashlib
from importlib import import_module
from typing import Any, Dict, List, Optional, Tuple

from app.plugins import _PluginBase
from app.runtime.cache import TTLCache
from app.runtime.log import logger

# 主程序中写死的失败原因占位文案，命中时用真实原因替换
PLACEHOLDER_ERROR_MESSAGES = (
    "下载种子内容为空",
    "未知原因",
)

# 取种失败原因缓存：区域名、容量与有效期
ERROR_CACHE_REGION = "downloadfailurecooldown_errors"
ERROR_CACHE_MAXSIZE = 512
ERROR_CACHE_TTL_SECONDS = 6 * 60 * 60

# 冷却分钟数允许范围
MIN_COOLDOWN_MINUTES = 0
MAX_COOLDOWN_MINUTES = 24 * 60


class DownloadFailureCooldown(_PluginBase):
    """下载失败冷却调优插件。"""

    # 插件名称
    plugin_name = "下载失败冷却调优"
    # 插件描述
    plugin_desc = "让下载失败的冷却时长可配置、按下载链接区分冷却，并如实记录真实失败原因。"
    # 插件图标
    plugin_icon = "downloadfailurecooldown.png"
    # 插件版本
    plugin_version = "1.0.0"
    # 插件作者
    plugin_author = "Afushu"
    # 作者主页
    author_url = "https://github.com/Afushu"
    # 插件配置项ID前缀
    plugin_config_prefix = "downloadfailurecooldown_"
    # 加载顺序
    plugin_order = 98
    # 可使用的用户级别
    auth_level = 1

    # 是否启用
    _enabled = False
    # 资源级失败冷却分钟数
    _resource_cooldown_minutes = 30
    # 瞬时失败冷却分钟数
    _transient_cooldown_minutes = 60
    # 是否把下载链接纳入冷却指纹
    _link_fingerprint = True
    # 是否如实记录真实失败原因
    _real_error_message = True
    # 补丁是否已应用
    _patch_applied = False
    # 取种失败原因缓存
    _error_cache: Optional[TTLCache] = None
    # 原始方法引用，用于停用时还原
    _originals: Dict[str, Any] = {}

    def init_plugin(self, config: dict = None) -> None:
        """读取插件配置，并应用或还原运行时补丁。"""
        self._restore_patch()
        self._enabled = False
        if not config:
            return
        self._enabled = bool(config.get("enabled"))
        self._resource_cooldown_minutes = self._clamp_minutes(
            config.get("resource_cooldown_minutes"), 30
        )
        self._transient_cooldown_minutes = self._clamp_minutes(
            config.get("transient_cooldown_minutes"), 60
        )
        self._link_fingerprint = config.get("link_fingerprint", True) is not False
        self._real_error_message = config.get("real_error_message", True) is not False
        if not self._enabled:
            logger.info("【下载失败冷却调优】插件未启用，保持主程序原始行为")
            return
        self._apply_patch()

    def get_state(self) -> bool:
        """获取插件启用状态。"""
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """返回插件远程命令列表。"""
        return []

    def get_api(self) -> List[Dict[str, Any]]:
        """返回插件 API 列表。"""
        return []

    def get_form(self) -> Tuple[Optional[List[dict]], Dict[str, Any]]:
        """返回插件配置表单与默认配置。"""
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enabled",
                                            "label": "启用插件",
                                            "hint": "启用后立即对下载链应用补丁，无需重启",
                                            "persistent-hint": True,
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "resource_cooldown_minutes",
                                            "label": "资源级失败冷却（分钟）",
                                            "type": "number",
                                            "min": MIN_COOLDOWN_MINUTES,
                                            "max": MAX_COOLDOWN_MINUTES,
                                            "hint": "下载链接失效、种子被删或被替换等；主程序固定 1440，0 表示不冷却",
                                            "persistent-hint": True,
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "transient_cooldown_minutes",
                                            "label": "瞬时失败冷却（分钟）",
                                            "type": "number",
                                            "min": MIN_COOLDOWN_MINUTES,
                                            "max": MAX_COOLDOWN_MINUTES,
                                            "hint": "网络超时、下载器异常等；主程序固定 60，0 表示不冷却",
                                            "persistent-hint": True,
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "link_fingerprint",
                                            "label": "按下载链接区分冷却",
                                            "hint": "开启后站点重新签发的有效链接不再被旧链接的失败记录拦住",
                                            "persistent-hint": True,
                                        },
                                    }
                                ],
                            },
                            {
                                "component": "VCol",
                                "props": {"cols": 12, "md": 6},
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "real_error_message",
                                            "label": "记录真实失败原因",
                                            "hint": "开启后冷却记录里写真实错误，例如「下载种子出错，状态码：404」",
                                            "persistent-hint": True,
                                        },
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {"cols": 12},
                                "content": [
                                    {
                                        "component": "VAlert",
                                        "props": {
                                            "type": "info",
                                            "variant": "tonal",
                                            "text": (
                                                "插件仅在启用时生效；停用后自动还原主程序原始逻辑。"
                                                "冷却记录中的历史数据保留，不受影响。"
                                            ),
                                        },
                                    }
                                ],
                            }
                        ],
                    },
                ],
            }
        ], {
            "enabled": False,
            "resource_cooldown_minutes": 30,
            "transient_cooldown_minutes": 60,
            "link_fingerprint": True,
            "real_error_message": True,
        }

    def get_page(self) -> Optional[List[dict]]:
        """返回插件详情页面。"""
        if not self._enabled:
            return [
                {
                    "component": "VAlert",
                    "props": {
                        "type": "warning",
                        "variant": "tonal",
                        "text": "插件未启用，当前使用主程序原始冷却逻辑（资源级 1440 分钟、瞬时 60 分钟）。",
                    },
                }
            ]
        return [
            {
                "component": "VAlert",
                "props": {
                    "type": "success",
                    "variant": "tonal",
                    "text": (
                        f"补丁已应用：资源级冷却 {self._resource_cooldown_minutes} 分钟，"
                        f"瞬时冷却 {self._transient_cooldown_minutes} 分钟；"
                        f"下载链接纳入指纹：{'是' if self._link_fingerprint else '否'}；"
                        f"记录真实失败原因：{'是' if self._real_error_message else '否'}。"
                    ),
                },
            }
        ]

    def stop_service(self) -> None:
        """停止插件并还原主程序原始方法。"""
        self._restore_patch()

    @staticmethod
    def _clamp_minutes(raw: Any, default: int) -> int:
        """把配置值规范为合法的冷却分钟数。"""
        try:
            minutes = int(raw)
        except (TypeError, ValueError):
            return default
        if minutes < MIN_COOLDOWN_MINUTES:
            return default
        return min(minutes, MAX_COOLDOWN_MINUTES)

    def _error_store(self) -> TTLCache:
        """获取取种失败原因缓存。"""
        if self._error_cache is None:
            self._error_cache = TTLCache(
                region=ERROR_CACHE_REGION,
                maxsize=ERROR_CACHE_MAXSIZE,
                ttl=ERROR_CACHE_TTL_SECONDS,
            )
        return self._error_cache

    @staticmethod
    def _link_digest(torrent: Any) -> str:
        """计算种子下载链接的短摘要，只用于指纹，不落库原始链接。"""
        url = getattr(torrent, "enclosure", None) if torrent else None
        if not url:
            return ""
        return hashlib.sha256(str(url).encode("utf-8")).hexdigest()[:16]

    def _real_error(self, context: Any) -> Optional[str]:
        """按当前候选的下载链接读取真实取种失败原因。"""
        torrent = getattr(context, "torrent_info", None)
        url = getattr(torrent, "enclosure", None) if torrent else None
        if not url:
            return None
        error_msg = self._error_store().get(str(url))
        return str(error_msg) if error_msg else None

    def _apply_patch(self) -> None:
        """对下载链的冷却相关方法应用运行时补丁。"""
        if self._patch_applied:
            logger.debug("【下载失败冷却调优】补丁已应用，跳过")
            return
        try:
            failure_module = import_module("app.chain.download.failure")
            owner = failure_module.DownloadFailureOwner
            torrent_module = import_module("app.application.torrent.download")
            helper = torrent_module.TorrentHelper
        except Exception as err:  # pylint: disable=broad-except
            logger.error(f"【下载失败冷却调优】补丁目标导入失败：{err}")
            return

        resource_default = int(
            getattr(failure_module, "DOWNLOAD_FAILURE_RESOURCE_TTL_SECONDS", 24 * 60 * 60)
        )
        originals: Dict[str, Any] = {}

        # 1. 冷却时长改为读取插件配置
        original_ttl = owner.__dict__.get("_download_failure_ttl")
        if original_ttl is not None:
            original_ttl_func = getattr(original_ttl, "__func__", original_ttl)
            plugin_self = self

            def patched_ttl(error_msg: Optional[str] = None) -> int:
                """按失败档位返回插件配置的冷却秒数。"""
                base = original_ttl_func(error_msg)
                if base == resource_default:
                    return plugin_self._resource_cooldown_minutes * 60
                return plugin_self._transient_cooldown_minutes * 60

            originals["ttl"] = original_ttl
            setattr(owner, "_download_failure_ttl", staticmethod(patched_ttl))

        # 2. 冷却指纹纳入下载链接摘要
        if self._link_fingerprint:
            original_fp = owner.__dict__.get("_build_download_failure_fingerprint")
            if original_fp is not None:
                original_fp_func = getattr(original_fp, "__func__", original_fp)
                plugin_self = self

                def patched_fingerprint(cls, context: Any) -> Optional[str]:
                    """在原指纹基础上追加下载链接摘要，避免新链接被旧失败拦住。"""
                    base = original_fp_func(cls, context)
                    if not base:
                        return base
                    digest = plugin_self._link_digest(
                        getattr(context, "torrent_info", None)
                    )
                    if not digest:
                        return base
                    combined = f"{base}:{digest}"
                    return hashlib.sha256(combined.encode("utf-8")).hexdigest()

                originals["fingerprint"] = original_fp
                setattr(
                    owner,
                    "_build_download_failure_fingerprint",
                    classmethod(patched_fingerprint),
                )

        # 3. 取种真实失败原因记录 + 冷却记录原因替换
        original_download = helper.__dict__.get("download_torrent")
        if original_download is not None:
            plugin_self = self

            def patched_download_torrent(self_helper: Any, url: str, *args: Any, **kwargs: Any) -> Any:
                """包装取种方法，把真实失败原因按链接记入缓存。"""
                result = original_download(self_helper, url, *args, **kwargs)
                try:
                    if url and isinstance(result, tuple) and len(result) >= 5:
                        error_msg = result[4]
                        if error_msg:
                            plugin_self._error_store()[str(url)] = str(error_msg)
                except Exception as err:  # pylint: disable=broad-except
                    logger.debug(f"【下载失败冷却调优】记录取种失败原因异常：{err}")
                return result

            originals["download_torrent"] = original_download
            setattr(helper, "download_torrent", patched_download_torrent)

        if self._real_error_message:
            original_record = owner.__dict__.get("_record_download_failure")
            if original_record is not None:
                plugin_self = self

                def patched_record(self_owner: Any, context: Any, error_msg: Optional[str] = None,
                                   *args: Any, **kwargs: Any) -> Any:
                    """写入冷却记录前，用真实失败原因替换占位文案。"""
                    real_error = plugin_self._real_error(context)
                    if real_error and (
                        not error_msg or str(error_msg) in PLACEHOLDER_ERROR_MESSAGES
                    ):
                        error_msg = real_error
                    return original_record(self_owner, context, error_msg, *args, **kwargs)

                originals["record"] = original_record
                setattr(owner, "_record_download_failure", patched_record)

        self._originals = originals
        self._patch_applied = True
        logger.info(
            "【下载失败冷却调优】补丁已应用："
            f"资源级冷却 {self._resource_cooldown_minutes} 分钟，"
            f"瞬时冷却 {self._transient_cooldown_minutes} 分钟，"
            f"链接指纹 {'开' if self._link_fingerprint else '关'}，"
            f"真实原因 {'开' if self._real_error_message else '关'}"
        )

    def _restore_patch(self) -> None:
        """还原主程序原始方法。"""
        if not self._patch_applied and not self._originals:
            return
        try:
            failure_module = import_module("app.chain.download.failure")
            owner = failure_module.DownloadFailureOwner
            torrent_module = import_module("app.application.torrent.download")
            helper = torrent_module.TorrentHelper
            if "ttl" in self._originals:
                setattr(owner, "_download_failure_ttl", self._originals["ttl"])
            if "fingerprint" in self._originals:
                setattr(
                    owner,
                    "_build_download_failure_fingerprint",
                    self._originals["fingerprint"],
                )
            if "record" in self._originals:
                setattr(owner, "_record_download_failure", self._originals["record"])
            if "download_torrent" in self._originals:
                setattr(helper, "download_torrent", self._originals["download_torrent"])
            logger.info("【下载失败冷却调优】补丁已还原")
        except Exception as err:  # pylint: disable=broad-except
            logger.error(f"【下载失败冷却调优】还原补丁失败：{err}")
        finally:
            self._originals = {}
            self._patch_applied = False

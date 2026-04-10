# MoviePilot v2 媒体管理插件
# 基于现有的媒体管理系统

from app.core.plugin import PluginManager
from app.plugins import _PluginBase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MediaManager(_PluginBase):
    """媒体管理插件"""

    # 插件元数据
    plugin_name = "媒体管理"
    plugin_desc = "媒体资源管理和播放插件，支持多网盘集成、STRM文件生成和视频播放"
    plugin_icon = "folder-movie"
    plugin_version = "1.0.9"
    plugin_author = "Afushu"
    plugin_author_link = "https://github.com/Afushu/MoviePilot-Plugins"
    
    # 插件配置项
    config_schema = {
        "enable": {
            "label": "启用插件",
            "type": "boolean",
            "default": True
        },
        "api_key": {
            "label": "API Key",
            "type": "string",
            "default": "",
            "required": False
        },
        "debug": {
            "label": "调试模式",
            "type": "boolean",
            "default": False
        }
    }
    
    def __init__(self):
        """初始化插件"""
        super().__init__()
        self.config = {}
        self.enabled = True
    
    def init_plugin(self, config: dict = None):
        """初始化插件功能"""
        self.config = config or {}
        self.enabled = self.config.get("enable", True)
        logger.info("MediaManager插件初始化完成")

    def get_state(self) -> bool:
        return self.enabled

    @staticmethod
    def get_command() -> list:
        pass

    def get_api(self) -> list:
        """获取插件API"""
        from .routes import mediamanager_index, test_endpoint, generate_strm, transfer_files, search_douban, get_disk_list, get_auth_qrcode, check_auth_status
        return [
            {"path": "/mediamanager", "endpoint": mediamanager_index, "methods": ["GET"]},
            {"path": "/api/mediamanager/test", "endpoint": test_endpoint, "methods": ["GET"]},
            {"path": "/api/mediamanager/strm/generate", "endpoint": generate_strm, "methods": ["POST"]},
            {"path": "/api/mediamanager/transfer", "endpoint": transfer_files, "methods": ["POST"]},
            {"path": "/api/mediamanager/douban/search", "endpoint": search_douban, "methods": ["GET"]},
            {"path": "/api/mediamanager/disk/list", "endpoint": get_disk_list, "methods": ["GET"]},
            {"path": "/api/mediamanager/auth/qrcode", "endpoint": get_auth_qrcode, "methods": ["GET"]},
            {"path": "/api/mediamanager/auth/status", "endpoint": check_auth_status, "methods": ["GET"]}
        ]

    def get_form(self) -> tuple:
        """
        组装插件配置页面
        """
        return [
            {
                "component": "VForm",
                "content": [
                    {
                        "component": "VRow",
                        "content": [
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12,
                                    "md": 6
                                },
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "enable",
                                            "label": "启用插件",
                                        }
                                    }
                                ]
                            },
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12,
                                    "md": 6
                                },
                                "content": [
                                    {
                                        "component": "VTextField",
                                        "props": {
                                            "model": "api_key",
                                            "label": "API Key",
                                            "placeholder": "请输入API Key（可选）",
                                            "clearable": True
                                        }
                                    }
                                ]
                            },
                            {
                                "component": "VCol",
                                "props": {
                                    "cols": 12,
                                    "md": 6
                                },
                                "content": [
                                    {
                                        "component": "VSwitch",
                                        "props": {
                                            "model": "debug",
                                            "label": "调试模式",
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ], {
            "enable": True,
            "api_key": "",
            "debug": False
        }

    def get_page(self) -> list:
        """
        插件的详情页面组件，支持VUE3语法和Vuetify3组件
        """
        return [
            {
                "component": "div",
                "content": [
                    {
                        "component": "v-alert",
                        "props": {
                            "type": "info",
                            "variant": "tonal",
                            "class": "mb-4",
                            "text": "此插件的媒体管理功能请访问 /mediamanager 操作。"
                        }
                    }
                ]
            }
        ]

# 注册插件
PluginManager.register(MediaManager)

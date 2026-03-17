# MoviePilot v2 媒体管理插件
# 基于现有的媒体管理系统

from app.core.plugin import PluginManager
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MediaManagerPlugin:
    """媒体管理插件"""
    
    # 插件元数据
    plugin_name = "mediamanager"
    plugin_version = "1.0.8"
    plugin_description = "媒体资源管理和播放插件，支持多网盘集成、STRM文件生成和视频播放"
    plugin_author = "Afushu"
    plugin_homepage = "https://github.com/Afushu/MoviePilot-Plugins"
    
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
        self.config = {}
        self.enabled = True
        logger.info(f"MediaManager插件初始化: 启用")
    
    def initialize(self):
        """初始化插件功能"""
        logger.info("MediaManager插件初始化完成")
    
    def get_routes(self):
        """获取插件路由"""
        from .routes import router
        return router
    
    def get_menu_items(self):
        """获取菜单项"""
        return [
            {
                "name": "媒体管理",
                "path": "/mediamanager",
                "icon": "folder-movie",
                "order": 100
            }
        ]
    
    def get_api_endpoints(self):
        """获取API端点"""
        return [
            {
                "path": "/api/mediamanager",
                "methods": ["GET", "POST"],
                "description": "媒体管理API"
            }
        ]

# 注册插件
PluginManager.register(MediaManagerPlugin())

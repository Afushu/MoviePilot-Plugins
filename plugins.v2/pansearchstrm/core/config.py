"""插件配置模型：搜索渠道、115 账号、转存与 STRM 目标。"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PanSouConfig(BaseModel):
    """盘搜渠道配置。"""

    enabled: bool = False
    base_url: str = Field(default="https://pansou.cc", description="盘搜服务地址")
    username: str = ""
    password: str = ""
    result_limit: int = Field(default=20, ge=1, le=100)
    timeout: int = Field(default=30, ge=5, le=120)


class JuyingConfig(BaseModel):
    """聚影渠道配置。"""

    enabled: bool = False
    base_url: str = Field(default="https://www.jying.top", description="聚影站点地址")
    username: str = ""
    password: str = ""
    result_limit: int = Field(default=20, ge=1, le=100)
    timeout: int = Field(default=30, ge=5, le=120)


class TelegramConfig(BaseModel):
    """Telegram 渠道配置（用户账号 + 扫码授权）。"""

    enabled: bool = False
    api_id: str = Field(default="", description="my.telegram.org 申请的 api_id")
    api_hash: str = Field(default="", description="my.telegram.org 申请的 api_hash")
    channels: List[str] = Field(default_factory=list, description="要搜索的频道用户名列表")
    search_global: bool = Field(default=False, description="是否额外做全局消息搜索")
    result_limit: int = Field(default=20, ge=1, le=100)
    timeout: int = Field(default=30, ge=5, le=120)


class P115Config(BaseModel):
    """115 网盘配置。"""

    cookies: str = Field(default="", description="115 登录 Cookie，扫码授权后自动写入")
    receive_path: str = Field(default="/网盘搜索转存", description="转存目标目录")
    share_duration: int = Field(default=-1, description="分享有效期天数，-1 为长期")
    auto_renewal: bool = True
    request_timeout: int = Field(default=60, ge=10, le=300)


class StrmConfig(BaseModel):
    """STRM 生成配置。"""

    enabled: bool = True
    output_path: str = Field(default="/media/网盘/STRM", description="STRM 输出目录")
    url_mode: str = Field(default="redirect", description="redirect=插件跳转端点，share=分享链接")
    media_ext: str = "mp4,mkv,ts,iso,m2ts,avi,rmvb,flv,mov,wmv"
    overwrite: bool = False


class PanSearchStrmConfig(BaseModel):
    """插件完整配置。"""

    enabled: bool = False
    notify: bool = True
    moviepilot_address: str = Field(default="", description="MoviePilot 访问地址，用于拼跳转端点")
    search_inject_enabled: bool = Field(
        default=True, description="是否把网盘资源并入默认「搜索资源」结果"
    )
    pansou: PanSouConfig = Field(default_factory=PanSouConfig)
    juying: JuyingConfig = Field(default_factory=JuyingConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    p115: P115Config = Field(default_factory=P115Config)
    strm: StrmConfig = Field(default_factory=StrmConfig)

    @classmethod
    def from_dict(cls, raw: Optional[Dict[str, Any]]) -> "PanSearchStrmConfig":
        """把插件配置字典安全地转换为配置模型。"""
        if not raw:
            return cls()
        try:
            return cls.model_validate(raw)
        except Exception:
            return cls()

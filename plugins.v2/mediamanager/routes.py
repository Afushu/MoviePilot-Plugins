# 插件路由文件
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.core.config import settings
import os
import logging
from .services import MediaManagerService

logger = logging.getLogger(__name__)

router = APIRouter()
service = MediaManagerService()

@router.get("/mediamanager", response_class=HTMLResponse)
async def mediamanager_index():
    """媒体管理首页"""
    try:
        # 读取前端HTML文件
        template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"加载媒体管理首页失败: {str(e)}")
        return HTMLResponse(content=f"<h1>媒体管理插件</h1><p>页面加载失败: {str(e)}</p>")

@router.get("/api/mediamanager/test")
async def test_endpoint():
    """测试API端点"""
    return JSONResponse(content={"message": "MediaManager插件API测试成功", "status": "ok"})

@router.post("/api/mediamanager/strm/generate")
async def generate_strm(data: dict):
    """生成STRM文件"""
    try:
        url = data.get("url")
        media_type = data.get("media_type", "movie")
        disk_type = data.get("disk_type", "p115")
        
        result = await service.generate_strm(url, media_type, disk_type)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"生成STRM文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/mediamanager/transfer")
async def transfer_files(data: dict):
    """转存文件"""
    try:
        url = data.get("url")
        disk_type = data.get("disk_type", "p115")
        
        result = await service.transfer_files(url, disk_type)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"转存文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/mediamanager/douban/search")
async def search_douban(keyword: str):
    """搜索豆瓣数据"""
    try:
        result = await service.search_douban(keyword)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"搜索豆瓣数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/mediamanager/disk/list")
async def get_disk_list(disk_type: str):
    """获取网盘文件列表"""
    try:
        result = await service.get_disk_list(disk_type)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"获取网盘文件列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

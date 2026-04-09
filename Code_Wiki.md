# MoviePilot-Plugins 代码维基 (Code Wiki)

欢迎来到 **MoviePilot-Plugins** 项目代码维基。本项目是一个针对 MoviePilot v2 的插件集合，目前主要包含了 **MediaManager**（媒体管理）插件。本文档将从整体架构、模块职责、关键类与函数、依赖关系以及运行方式等方面，详细介绍该项目的结构与核心逻辑。

---

## 1. 项目整体架构

项目主要围绕 [MoviePilot v2](https://github.com/jxxghp/MoviePilot) 的插件系统开发。通过继承和实现 MoviePilot 的插件基类，向主程序注入新的路由、页面、菜单和后台服务。

**架构分层：**
- **元数据层**：`plugins.json` / `package.json` / `package.v2.json` 提供插件市场的描述信息，方便 MoviePilot 识别并一键安装。
- **入口与配置层 (`__init__.py`)**：负责插件初始化、配置项定义、路由挂载和菜单注入。
- **接口路由层 (`routes.py`)**：基于 FastAPI 定义前后端交互的 API 接口，以及前端页面的渲染入口。
- **业务服务层 (`services.py`)**：处理核心的业务逻辑，包括生成 STRM 文件、文件转存、豆瓣搜索等，隔离了业务实现和接口控制。
- **视图展示层 (`templates/`)**：提供前端交互的 HTML/JS/CSS 页面结构，为用户提供可视化的插件管理面板。

---

## 2. 主要模块职责

项目目录结构如下：

```text
/workspace
├── package.json           # 插件元数据（旧版/兼容）
├── package.v2.json        # 插件元数据 v2
├── plugins.v2/
│   ├── plugins.json       # 插件索引清单
│   └── mediamanager/      # MediaManager 核心插件目录
│       ├── __init__.py    # 插件入口，定义插件类并注册
│       ├── routes.py      # API 接口及页面路由控制器
│       ├── services.py    # 业务逻辑服务层
│       ├── templates/
│       │   └── index.html # 前端管理面板 HTML 模板
│       └── README.md      # 插件专属说明文档
├── README.md              # 项目根目录说明
└── LICENSE                # 开源许可证
```

### 核心模块职责说明
*   **[__init__.py](file:///workspace/plugins.v2/mediamanager/__init__.py)**：**插件核心入口**。定义了 `MediaManagerPlugin` 类，声明了插件的基础信息（名称、版本、描述）和配置模式（Schema）。负责向 MoviePilot 的 `PluginManager` 注册当前插件，注入侧边栏菜单（`get_menu_items`），并挂载 API 路由。
*   **[routes.py](file:///workspace/plugins.v2/mediamanager/routes.py)**：**请求控制器**。利用 FastAPI 的 `APIRouter` 构建 HTTP 接口，接受前端请求并调用 `services.py` 中的方法。包含了 HTML 页面下发（`/mediamanager`）及一系列数据接口（`/api/mediamanager/...`）。
*   **[services.py](file:///workspace/plugins.v2/mediamanager/services.py)**：**业务服务提供者**。实现了如 STRM 文件生成、各大网盘（115、123、夸克）的文件转存以及豆瓣影视数据搜索的具体逻辑封装。
*   **[templates/index.html](file:///workspace/plugins.v2/mediamanager/templates/index.html)**：**用户界面**。MoviePilot 媒体管理插件的 Web UI 页面。

---

## 3. 关键类与函数说明

### 3.1 插件入口类 (`__init__.py`)
**`class MediaManagerPlugin`**
*   **属性**: 
    *   `config_schema`: 定义了插件的配置项表单，包含 `enable` (启用插件)、`api_key` (API密钥)、`debug` (调试模式)。
*   **方法**:
    *   `__init__(self)`: 初始化插件配置与状态。
    *   `initialize(self)`: 插件生命周期函数，在 MoviePilot 加载插件时调用以执行初始化操作。
    *   `get_routes(self)`: 暴露插件路由，返回 `routes.py` 中定义的 `router`。
    *   `get_menu_items(self)`: 注入 MoviePilot 的侧边栏菜单项（名称为“媒体管理”，图标 `folder-movie`）。
    *   `get_api_endpoints(self)`: 返回供主程序识别的 API 列表与说明。

### 3.2 路由控制器 (`routes.py`)
**FastAPI 路由接口**
*   `mediamanager_index()` -> `GET /mediamanager`: 读取并返回 `templates/index.html`，作为插件的后台管理主界面。
*   `generate_strm(data: dict)` -> `POST /api/mediamanager/strm/generate`: 接收 JSON 参数（url, media_type, disk_type），调用 service 层的 STRM 生成服务。
*   `transfer_files(data: dict)` -> `POST /api/mediamanager/transfer`: 接收 JSON 参数（url, disk_type），调用 service 层执行指定网盘的文件转存。
*   `search_douban(keyword: str)` -> `GET /api/mediamanager/douban/search`: 接收 URL 参数 `keyword`，调用 service 层查询豆瓣匹配的影视信息。

### 3.3 服务逻辑层 (`services.py`)
**`class MediaManagerService`**
*   `generate_strm(self, url: str, media_type: str, disk_type: str)`: 核心功能函数。负责解析分享链接，并生成指向媒体流的 STRM 伪装文件。
*   `transfer_files(self, url: str, disk_type: str)`: 核心功能函数。负责将第三方网盘分享链接的文件自动转存至绑定的对应网盘（如 p115, quark 等）。
*   `search_douban(self, keyword: str)`: 调用豆瓣接口（或内置逻辑）搜索相关影视作品的元数据（标题、年份、ID、类型等）。
*   `get_disk_list(self, disk_type: str)`: 获取特定类型网盘下的文件和目录列表。

---

## 4. 依赖关系

本插件为基于 Python 的服务端项目，运行于 MoviePilot v2 宿主环境中，依赖以下核心库：

*   **[MoviePilot v2.0+](https://github.com/jxxghp/MoviePilot)**: 宿主系统。使用了 `app.core.plugin.PluginManager` 注册插件机制，以及 `app.core.config.settings` 获取全局配置。
*   **[FastAPI](https://fastapi.tiangolo.com/)**: 用于构建 API 和暴露路由，项目使用 `APIRouter`, `HTMLResponse`, `JSONResponse`, `HTTPException` 等模块。
*   **[httpx](https://www.python-httpx.org/)**: 高性能异步 HTTP 客户端，在 `services.py` 中被用来请求第三方网络资源（如豆瓣 API、网盘 API 等）。
*   **标准库**: `logging`, `json` 等。

---

## 5. 项目运行与构建方式

该项目为免编译的 Python 插件，无需独立的 Build 流程，需挂载或安装在 MoviePilot v2 主系统中运行。

### 5.1 方式一：通过插件市场安装 (推荐)
1. 登录 MoviePilot 管理后台。
2. 导航至 **"设置" -> "插件市场"**。
3. 在 **"插件仓库地址"** 中添加本项目地址：`https://github.com/Afushu/MoviePilot-Plugins`
4. 点击"保存"并刷新列表，找到 **MediaManager** 并点击"安装"。

### 5.2 方式二：手动部署
1. 下载本项目源码。
2. 将项目中的 `plugins.v2/mediamanager` 整个目录复制或映射到 MoviePilot 运行目录下的 `plugins.v2/` 目录中。
3. 重启 MoviePilot 服务：
   ```bash
   # 如果使用 Docker
   docker restart moviepilot
   ```
4. 在 MoviePilot Web 界面中进入插件管理，开启 `MediaManager` 插件。
5. 刷新页面，在左侧导航栏点击 **"媒体管理"** 即可进入插件操作面板。

### 5.3 开发与调试
*   打开 MoviePilot 插件配置页面，将 MediaManager 的 `debug`（调试模式）设置为 `True`。
*   查看 MoviePilot 的运行日志，过滤 `mediamanager` 相关的 `logger` 输出，以便跟踪 API 响应与业务处理流程。

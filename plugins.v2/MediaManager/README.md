# MediaManager 插件

MediaManager是一个MoviePilot v2的媒体管理插件，支持多网盘集成、STRM文件生成和视频播放功能。

## 功能特性

- **多网盘集成**：支持115网盘、123网盘、夸克网盘
- **STRM文件生成**：从分享链接生成STRM文件
- **文件转存**：批量转存文件到指定网盘
- **豆瓣搜索**：搜索豆瓣影视数据
- **网盘管理**：查看和管理网盘文件

## 安装方法

1. 将`MediaManager`目录复制到MoviePilot的`plugins.v2`目录下
2. 重启MoviePilot服务
3. 在MoviePilot管理界面中启用插件

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| enable | boolean | true | 是否启用插件 |
| api_key | string | "" | API密钥（可选） |
| debug | boolean | false | 是否启用调试模式 |

## 使用方法

1. 在MoviePilot导航栏中点击"媒体管理"进入插件界面
2. 选择需要的功能标签页：
   - **STRM生成**：输入分享链接，选择媒体类型和网盘类型，点击生成
   - **文件转存**：输入分享链接，选择目标网盘，点击转存
   - **豆瓣搜索**：输入关键词搜索豆瓣影视数据
   - **网盘管理**：查看网盘文件列表

## API接口

### 生成STRM文件
- **路径**：`/api/mediamanager/strm/generate`
- **方法**：POST
- **参数**：
  - url: 分享链接
  - media_type: 媒体类型（movie/tv/music）
  - disk_type: 网盘类型（p115/p123/quark）
- **返回**：STRM文件生成结果

### 文件转存
- **路径**：`/api/mediamanager/transfer`
- **方法**：POST
- **参数**：
  - url: 分享链接
  - disk_type: 目标网盘类型
- **返回**：转存结果

### 豆瓣搜索
- **路径**：`/api/mediamanager/douban/search`
- **方法**：GET
- **参数**：
  - keyword: 搜索关键词
- **返回**：搜索结果

## 依赖说明

- MoviePilot v2.0+
- FastAPI
- httpx

## 注意事项

1. 请确保已正确配置各网盘的账号信息
2. 生成STRM文件时，请确保目标目录存在且有写入权限
3. 转存文件时，请注意网盘空间是否充足
4. 豆瓣搜索功能可能受到API限制，请合理使用

## 故障排除

- **插件无法加载**：检查插件目录结构是否正确，确保MoviePilot版本兼容
- **STRM生成失败**：检查分享链接是否有效，目标目录是否可写
- **转存失败**：检查网盘账号是否登录，空间是否充足
- **豆瓣搜索失败**：检查网络连接，可能是API限制导致

## 更新日志

### v1.0.0
- 初始版本
- 支持115网盘、123网盘、夸克网盘
- 实现STRM生成、文件转存、豆瓣搜索功能
- 提供Web界面管理

## 贡献

欢迎提交Issue和Pull Request来改进这个插件。

## 许可证

MIT License

## 作者

Afushu

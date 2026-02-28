# AI助手本地服务

基于Python + Flask + 智谱AI的本地AI助手服务，支持多轮对话、对话管理和配置自定义。

## 功能特性

- ✅ AI对话功能 (使用智谱AI GLM-4)
- ✅ 多轮对话上下文管理
- ✅ 对话历史记录 (SQLite本地存储)
- ✅ 创建/删除/切换对话
- ✅ 配置管理 (API Key、模型、温度等)
- ✅ 简洁的Web界面

## 技术栈

- **后端**: Python 3.9+ + Flask
- **AI**: 智谱AI GLM-4
- **数据库**: SQLite
- **前端**: HTML + CSS + JavaScript (原生)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

首次启动后，在Web界面点击"配置"按钮，填入智谱AI API Key。

或设置环境变量：

```bash
export ZHIPU_API_KEY="your-api-key"
```

### 3. 运行服务

```bash
python app.py
```

服务默认运行在: http://127.0.0.1:5000

### 4. 使用界面

打开浏览器访问 http://127.0.0.1:5000，即可开始使用。

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPU_API_KEY` | 智谱AI API Key | - |
| `MODEL` | 模型名称 | `glm-4` |
| `TEMPERATURE` | 温度参数 (0-1) | `0.7` |
| `MAX_TOKENS` | 最大token数 | `2000` |
| `MAX_HISTORY_ROUNDS` | 历史对话轮数 | `10` |
| `SYSTEM_PROMPT` | 系统提示词 | `你是一个有用的AI助手。` |

### 智谱AI模型选择

- `glm-4` - 标准版 (推荐)
- `glm-4-flash` - 闪速版 (响应更快)
- `glm-4-air` - 轻量版 (成本更低)

更多模型信息请参考: [智谱AI文档](https://open.bigmodel.cn/dev/api)

## API接口

### 对话管理

```
GET    /api/conversations              # 获取对话列表
POST   /api/conversations              # 创建新对话
DELETE /api/conversations/<id>         # 删除对话
PUT    /api/conversations/<id>         # 更新对话标题
GET    /api/conversations/<id>/messages # 获取对话消息
```

### 消息发送

```
POST   /api/conversations/<id>/messages # 发送消息
```

### 配置管理

```
GET    /api/config                      # 获取配置
POST   /api/config                      # 更新配置
POST   /api/config/validate             # 验证API Key
```

## 项目结构

```
ai-assistant-local/
├── app.py                  # Flask主应用
├── config.py               # 配置管理
├── requirements.txt        # Python依赖
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── conversation.py
│   └── message.py
├── services/               # 业务服务
│   ├── __init__.py
│   ├── db_service.py      # 数据库服务
│   └── zhipu_service.py   # 智谱AI服务
├── templates/              # HTML模板
│   └── index.html
├── static/                 # 静态资源
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── data/                   # 数据存储 (SQLite)
│   └── assistant.db
└── README.md
```

## 使用示例

### 1. 创建对话并发送消息

```python
import requests

# 创建对话
response = requests.post('http://localhost:5000/api/conversations', json={
    'title': 'Python学习'
})
conversation_id = response.json()['id']

# 发送消息
response = requests.post(
    f'http://localhost:5000/api/conversations/{conversation_id}/messages',
    json={'content': '什么是Python装饰器？'}
)

result = response.json()
print(result['message']['content'])
```

### 2. 获取对话历史

```python
response = requests.get(
    f'http://localhost:5000/api/conversations/{conversation_id}/messages'
)
messages = response.json()['messages']
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")
```

## 数据存储

所有数据存储在SQLite数据库 `data/assistant.db` 中，包含三个表：

- `conversations` - 对话列表
- `messages` - 消息记录
- `config` - 配置存储

如需备份数据，直接复制 `data/assistant.db` 文件即可。

## 注意事项

1. **API Key安全**: 不要将API Key提交到代码仓库，使用环境变量或配置界面设置
2. **Token限制**: 注意智谱AI的API调用次数和Token限制
3. **数据备份**: 定期备份 `data/assistant.db` 文件
4. **上下文长度**: 历史对话轮数不宜过多，避免超过Token限制

## 故障排查

### 问题: 无法连接到智谱AI

**解决方案**:
1. 检查API Key是否正确
2. 检查网络连接
3. 确认智谱AI服务状态

### 问题: 数据库文件不存在

**解决方案**:
首次运行会自动创建数据库，确保 `data/` 目录有写权限。

### 问题: 端口被占用

**解决方案**:
修改 `config.py` 中的 `PORT` 变量，或设置环境变量 `PORT`。

## 后续计划

- [ ] 流式响应支持
- [ ] 文件上传与分析
- [ ] Markdown渲染
- [ ] 代码高亮
- [ ] 知识库检索 (RAG)
- [ ] 多用户支持

## 许可证

MIT License

## 联系方式

如有问题，请提 Issue。

---

*本项目为快速验证原型，适用于个人本地使用。*

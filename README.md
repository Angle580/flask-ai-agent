# AI Agent Demo（工具调用版）

一个用 Flask + 火山方舟（豆包大模型）写的**工具调用 Agent** 演示。
大模型自己判断什么时候该调工具、调哪个工具，拿到结果后再组织成自然语言回答。

## 它能干什么

在网页里和它对话，它会自动调用工具：

| 工具 | 作用 |
| --- | --- |
| `calculator` | 安全地算数学表达式（不会瞎编数字） |
| `get_time` | 获取当前时间 |
| `add_note` / `list_notes` | 记便签、查便签 |
| `get_weather` | 查天气（演示数据） |

比如你问：
- 「现在几点？顺便算一下 (123+456)*2」→ 它会先调 `get_time` 再调 `calculator`
- 「帮我记一下明天下午3点开组会」→ 调 `add_note`
- 「我都有哪些便签」→ 调 `list_notes`

网页里会用黄色小框把**每一步调了什么工具、参数、返回值**都展示出来，能清楚看到 Agent 的思考轨迹。

## 项目结构

```
ai-agent-demo/
├── app.py           # Flask 入口，/api/chat 接口
├── agent.py         # Agent 核心循环（LLM <-> 工具）
├── tools.py         # 工具实现 + 工具 schema
├── test_tools.py    # 工具单元测试
├── test_agent.py    # Agent 循环测试（mock 掉 LLM）
├── requirements.txt
└── templates/
    └── index.html   # 聊天网页
```

## 核心原理

```
用户提问
   ↓
[调 LLM] ──→ 要不要调工具？
   │            │
   │            ├─ 不要 → 返回最终答案
   │            │
   │            └─ 要 → 解析 tool_calls，执行对应函数
   │                       ↓
   │                 把工具结果喂回 LLM
   └──────────────────────┘
                          ↑
                  循环直到出最终答案（最多 8 步）
```

## 快速开始

```bash
pip install -r requirements.txt

# 设置你的 Ark API Key 和 endpoint ID（Windows PowerShell）
$env:ARK_API_KEY = "你的 ark-xxx"
$env:ARK_MODEL   = "你的 ep-xxx"

python app.py
# 浏览器打开 http://127.0.0.1:8080
```

> API Key 和 endpoint ID 从环境变量读，不要硬编码进代码。
> 也可以直接编辑 `agent.py` 顶部填默认值。

## 跑测试

```bash
python -m pytest test_tools.py test_agent.py -v
```

测试覆盖：
- 5 个工具函数的输入输出
- 恶意表达式被拦截
- Agent 直接回答（不调工具）
- Agent 调工具后再回答（mock LLM）
- 超过最大步数自动停止

## 怎么加新工具

1. 在 `tools.py` 写一个 Python 函数
2. 在 `TOOL_IMPL` 里注册名字
3. 在 `TOOL_SCHEMAS` 里加一段 JSON Schema 描述参数

不用改 `agent.py`，Agent 会自动发现新工具。

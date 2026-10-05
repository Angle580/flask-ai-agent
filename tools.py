"""Agent 可用的工具：每个工具 = 一份 JSON Schema + 一个 Python 函数。"""
import math
import re
from datetime import datetime

# 内存里的便签
_NOTES = []

# ---------- 工具实现 ----------
def calculator(expression: str) -> str:
    """安全地计算数学表达式"""
    # 只允许数字和基本运算符
    if not re.match(r'^[\d+\-*/().\s]+$', expression):
        return "错误：表达式只能包含数字和 + - * / ( )"
    try:
        # 用 eval 但限定命名空间
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return str(result)
    except Exception as e:
        return f"计算失败：{e}"

def get_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_note(content: str) -> str:
    """加一条便签"""
    _NOTES.append(content)
    return f"已保存，当前共 {len(_NOTES)} 条便签"

def list_notes() -> str:
    """列出所有便签"""
    if not _NOTES:
        return "还没有便签"
    return "\n".join(f"{i+1}. {n}" for i, n in enumerate(_NOTES))

def get_weather(city: str) -> str:
    """查询天气（模拟数据）"""
    return f"{city}：晴，22~28℃，东南风 2 级（演示数据）"

# ---------- 工具注册表 ----------
TOOL_IMPL = {
    "calculator": calculator,
    "get_time": get_time,
    "add_note": add_note,
    "list_notes": list_notes,
    "get_weather": get_weather,
}

# ---------- 给大模型看的 schema ----------
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，比如 123*45 或者 (3+5)/2",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前的日期和时间",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "保存一条用户便签/提醒",
            "parameters": {
                "type": "object",
                "properties": {"content": {"type": "string"}},
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "列出所有已保存的便签",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }
    },
]

def run_tool(name: str, args: dict) -> str:
    fn = TOOL_IMPL.get(name)
    if not fn:
        return f"未知工具：{name}"
    try:
        return fn(**args)
    except Exception as e:
        return f"工具执行出错：{e}"

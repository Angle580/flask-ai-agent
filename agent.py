"""Agent 核心循环：用户提问 -> 调 LLM -> 决定是否调工具 -> 执行 -> 再喂给 LLM -> 直到出最终答案"""
import json
import os
from openai import OpenAI
from tools import TOOL_SCHEMAS, run_tool

client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY", "在此填入你的 Ark API Key"),
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)
MODEL = os.environ.get("ARK_MODEL", "在此填入你的 ep-xxx 接入点 ID")

SYSTEM = """你是一个能调用工具的助手。需要算数就用 calculator，需要知道时间就用 get_time，
用户让你记东西就用 add_note，要看便签用 list_notes，问天气就用 get_weather。
不要自己瞎编数字，该调工具就调。回答用中文，简洁一点。"""

MAX_STEPS = 8  # 防止死循环

def run_agent(user_message: str, history: list | None = None):
    """跑一轮 agent，返回 (最终回复, 执行轨迹list)"""
    messages = [{"role": "system", "content": SYSTEM}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    trace = []  # 给前端展示用的每一步

    for step in range(MAX_STEPS):
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            # 没有工具调用，说明已经是最终答案
            trace.append({"type": "final", "content": msg.content})
            return msg.content, trace

        # 把助手这一轮（含 tool_calls）加进历史
        messages.append(msg.model_dump(exclude_none=True))

        # 逐个执行工具
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            trace.append({"type": "tool_call", "name": name, "args": args})
            result = run_tool(name, args)
            trace.append({"type": "tool_result", "name": name, "result": result})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return "（达到最大步数，停止）", trace

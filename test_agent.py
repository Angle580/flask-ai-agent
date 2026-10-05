"""Agent 循环测试 —— mock 掉大模型，只测流程"""
import json
from unittest.mock import patch, MagicMock
import agent


def _fake_message(content=None, tool_calls=None):
    m = MagicMock()
    m.content = content
    m.tool_calls = tool_calls
    return m


def test_agent_direct_answer():
    """模型直接回答，不调工具"""
    with patch.object(agent.client.chat.completions, 'create',
                      return_value=MagicMock(choices=[MagicMock(message=_fake_message("你好呀"))])):
        answer, trace = agent.run_agent("你好")
    assert "你好" in answer
    assert trace[-1]["type"] == "final"


def test_agent_tool_loop():
    """模型先调 calculator，再给最终答案"""
    tc = MagicMock()
    tc.function.name = "calculator"
    tc.function.arguments = '{"expression": "1+1"}'
    tc.id = "call_1"

    msg1 = _fake_message(tool_calls=[tc])
    msg2 = _fake_message(content="等于2")

    with patch.object(agent.client.chat.completions, 'create',
                      side_effect=[MagicMock(choices=[MagicMock(message=msg1)]),
                                   MagicMock(choices=[MagicMock(message=msg2)])]):
        answer, trace = agent.run_agent("1+1等于几")

    assert answer == "等于2"
    # trace 里应该有一次 tool_call + 一次 tool_result + final
    types = [t["type"] for t in trace]
    assert "tool_call" in types and "tool_result" in types and "final" in types


def test_agent_max_steps():
    """模型一直调工具，达到 MAX_STEPS 后停止"""
    tc = MagicMock()
    tc.function.name = "get_time"
    tc.function.arguments = '{}'
    tc.id = "x"
    msg = _fake_message(tool_calls=[tc])
    with patch.object(agent.client.chat.completions, 'create',
                      return_value=MagicMock(choices=[MagicMock(message=msg)])):
        answer, trace = agent.run_agent("一直调工具")
    assert "最大步数" in answer

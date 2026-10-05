"""工具函数的单元测试 —— 不需要调大模型"""
import tools


def test_calculator_basic():
    assert tools.calculator("1+2") == "3"
    assert tools.calculator("(123+456)*2") == "1158"

def test_calculator_rejects_evil():
    r = tools.calculator("__import__('os').system('dir')")
    assert "错误" in r or "失败" in r

def test_get_time_format():
    r = tools.get_time()
    assert len(r) == 19  # YYYY-MM-DD HH:MM:SS

def test_notes_crud():
    tools._NOTES.clear()
    assert "还没有" in tools.list_notes()
    r = tools.add_note("明天开会")
    assert "已保存" in r
    assert "明天开会" in tools.list_notes()

def test_weather():
    r = tools.get_weather("北京")
    assert "北京" in r

def test_run_tool_unknown():
    r = tools.run_tool("nonexistent", {})
    assert "未知" in r

def test_tool_schemas_valid():
    # 每个 schema 都必须有 name 和 parameters
    for s in tools.TOOL_SCHEMAS:
        fn = s["function"]
        assert "name" in fn
        assert "parameters" in fn
        assert fn["name"] in tools.TOOL_IMPL

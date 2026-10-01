from types import SimpleNamespace as NS

import pytest

from agent_template import Agent, Tool, calculator_tool
from agent_template.tools import safe_eval


def text(t):
    return NS(type="text", text=t)


def tool_use(id_, name, **inp):
    return NS(type="tool_use", id=id_, name=name, input=inp)


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})  # snapshot
        return self.responses.pop(0)


def test_returns_text_without_tools():
    client = FakeClient([NS(stop_reason="end_turn", content=[text("hi")])])
    assert Agent(client).run("hello") == "hi"
    assert "tools" not in client.calls[0]


def test_executes_tool_then_answers():
    client = FakeClient(
        [
            NS(stop_reason="tool_use", content=[tool_use("1", "calculator", expression="2+3")]),
            NS(stop_reason="end_turn", content=[text("5")]),
        ]
    )
    assert Agent(client, tools=[calculator_tool]).run("2+3?") == "5"
    result = client.calls[1]["messages"][-1]["content"][0]
    assert result["content"] == "5" and result["is_error"] is False


def test_tool_error_is_returned_not_raised():
    boom = Tool("boom", "x", {"type": "object", "properties": {}}, lambda: 1 / 0)
    client = FakeClient(
        [
            NS(stop_reason="tool_use", content=[tool_use("1", "boom")]),
            NS(stop_reason="end_turn", content=[text("recovered")]),
        ]
    )
    assert Agent(client, tools=[boom]).run("go") == "recovered"
    assert client.calls[1]["messages"][-1]["content"][0]["is_error"] is True


def test_unknown_tool_is_error():
    client = FakeClient(
        [
            NS(stop_reason="tool_use", content=[tool_use("1", "nope")]),
            NS(stop_reason="end_turn", content=[text("ok")]),
        ]
    )
    Agent(client).run("go")
    assert client.calls[1]["messages"][-1]["content"][0]["is_error"] is True


def test_max_turns_bounds_loop():
    looping = NS(stop_reason="tool_use", content=[tool_use("1", "calculator", expression="1")])
    client = FakeClient([looping] * 3)
    with pytest.raises(RuntimeError):
        Agent(client, tools=[calculator_tool], max_turns=3).run("loop")


def test_safe_eval():
    assert safe_eval("0.125 * 480") == 60
    assert safe_eval("-2 ** 2") == -4
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('echo hi')")

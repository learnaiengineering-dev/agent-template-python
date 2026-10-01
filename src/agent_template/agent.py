"""A minimal tool-using agent loop."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Callable

DEFAULT_MODEL = os.environ.get("MODEL", "claude-sonnet-5-5")


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    fn: Callable[..., Any]

    def spec(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


class Agent:
    def __init__(
        self,
        client: Any,
        tools: list[Tool] | None = None,
        system: str = "You are a helpful assistant. Use tools when they help.",
        model: str = DEFAULT_MODEL,
        max_turns: int = 8,
        max_tokens: int = 1024,
    ) -> None:
        self.client = client
        self.tools = {t.name: t for t in (tools or [])}
        self.system = system
        self.model = model
        self.max_turns = max_turns
        self.max_tokens = max_tokens

    def run(self, user_message: str) -> str:
        messages: list[dict] = [{"role": "user", "content": user_message}]
        for _ in range(self.max_turns):
            kwargs: dict[str, Any] = dict(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system,
                messages=messages,
            )
            if self.tools:
                kwargs["tools"] = [t.spec() for t in self.tools.values()]
            resp = self.client.messages.create(**kwargs)
            messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")
            results = [self._call(b) for b in resp.content if b.type == "tool_use"]
            messages.append({"role": "user", "content": results})
        raise RuntimeError(f"Agent exceeded max_turns={self.max_turns}")

    def _call(self, block: Any) -> dict:
        tool = self.tools.get(block.name)
        if tool is None:
            return self._result(block.id, f"Unknown tool: {block.name}", True)
        try:
            return self._result(block.id, str(tool.fn(**block.input)), False)
        except Exception as exc:  # returned to the model so it can recover
            return self._result(block.id, f"{type(exc).__name__}: {exc}", True)

    @staticmethod
    def _result(tool_use_id: str, content: str, is_error: bool) -> dict:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content,
            "is_error": is_error,
        }


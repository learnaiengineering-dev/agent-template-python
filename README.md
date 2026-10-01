# agent-template-python

A minimal, production-minded **tool-using AI agent** in ~100 lines of Python, built on the Anthropic SDK. No framework, no magic: just the agent loop, a tool registry, error handling and tests you can read in ten minutes.

## What you get

- `Agent` class with a bounded tool-use loop (`max_turns`) so it can't run away
- `Tool` registry: write a plain function, attach a JSON schema
- Tool errors are returned to the model as `is_error` results instead of crashing
- Dependency-injected client, so tests run offline with a fake client
- Safe calculator tool (AST-based, no `eval`) as a worked example
- CLI: `python -m agent_template "What is 12.5% of 480?"`

## Quickstart

```bash
git clone https://github.com/learnaiengineering-dev/agent-template-python
cd agent-template-python
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export ANTHROPIC_API_KEY=sk-ant-...   # never commit this
python -m agent_template "What is 12.5% of 480?"
pytest -q
```

Set `MODEL` to override the default model.

## Adding a tool

```python
from agent_template import Tool

def word_count(text: str) -> int:
    return len(text.split())

word_count_tool = Tool(
    name="word_count",
    description="Count the words in a piece of text.",
    input_schema={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
    fn=word_count,
)
```

Pass it to `Agent(client, tools=[word_count_tool])`.

## Design notes

| Decision | Why |
|---|---|
| Bounded loop | Prevents infinite tool loops and runaway cost |
| Errors as tool results | Lets the model recover and retry instead of crashing |
| Injected client | Deterministic offline tests |
| No `eval` in calculator | Tool inputs are untrusted model output |

## Next steps (free, on the portal)

Work through the agents series and labs to extend this with memory, planning, guardrails and evals.

---

## Part of Learn AI Engineering

This repo is a free resource from [Learn AI Engineering](https://learnaiengineering.dev/?utm_source=github&utm_medium=repo&utm_campaign=agent-template-python) — *Build production AI systems.*

- Structured learning paths, labs and portfolio projects: [https://learnaiengineering.dev](https://learnaiengineering.dev/?utm_source=github&utm_medium=repo&utm_campaign=agent-template-python)
- Want the production-ready version (enterprise templates, deployment, evals, runbooks)? See the **FDE Toolkit** on the portal.
- More free repos: [github.com/learnaiengineering-dev](https://github.com/learnaiengineering-dev)

Licensed under MIT.

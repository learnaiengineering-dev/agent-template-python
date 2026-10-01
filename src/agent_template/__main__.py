import sys

import anthropic

from . import Agent, calculator_tool


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit('usage: python -m agent_template "your question"')
    agent = Agent(anthropic.Anthropic(), tools=[calculator_tool])
    print(agent.run(" ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()


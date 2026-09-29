"""AgentCore-friendly wrapper for the mock payment investigation agent.

This keeps the existing mock payment tool contracts intact while allowing the app
to be run as a containerized runtime entrypoint for AWS AgentCore or similar
managed execution environments.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


def run_agent(prompt: str) -> dict[str, Any]:
    """Run the payment agent against the current mock tool implementation."""
    from task2_payment_agent.agents.payment_agent.agent import build_agent

    agent = build_agent()
    response = agent(prompt)
    return {
        "prompt": prompt,
        "response": str(response),
        "model": os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-6"),
        "region": os.getenv("AWS_REGION", "us-east-1"),
    }


def main() -> None:
    """Simple CLI entrypoint for containerized deployments.

    Accepts either a direct CLI argument or JSON from stdin, for example:
        python -m task2_payment_agent.agentcore_runtime "Investigate supplier invoice INV1234"
        echo '{"prompt": "Investigate supplier invoice INV1234"}' | python -m task2_payment_agent.agentcore_runtime
    """
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            prompt = "Investigate supplier invoice INV1234"
        else:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                prompt = raw
            else:
                prompt = payload.get("prompt") or payload.get("input") or "Investigate supplier invoice INV1234"

    result = run_agent(prompt)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()

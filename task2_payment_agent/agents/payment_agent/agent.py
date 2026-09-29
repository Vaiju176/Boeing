"""Strands agent entry point for local payment investigation."""

from task2_payment_agent.agents.payment_agent.prompt import PAYMENT_AGENT_PROMPT
from task2_payment_agent.agents.payment_agent.tools import (
    get_due_date,
    get_payment_status,
    get_s4_invoice,
    get_transaction_id,
)


def build_agent():
    """Construct the Strands agent, importing the optional SDK on demand."""
    try:
        from strands import Agent
    except ImportError as exc:
        raise RuntimeError(
            "Strands is not installed. Install requirements-agent.txt first."
        ) from exc

    return Agent(
        system_prompt=PAYMENT_AGENT_PROMPT,
        tools=[get_s4_invoice, get_payment_status, get_transaction_id, get_due_date],
    )


def main() -> None:
    agent = build_agent()
    response = agent("Investigate supplier invoice INV1234")
    print(response)


if __name__ == "__main__":
    main()

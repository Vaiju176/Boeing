"""Single registry for payment tool names, descriptions, and implementations."""

from typing import Any, Callable, Dict

from task2_payment_agent.agents.payment_agent.tools import (
    get_due_date,
    get_payment_status,
    get_s4_invoice,
    get_transaction_id,
)

TOOLS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "get_s4_invoice": get_s4_invoice,
    "get_payment_status": get_payment_status,
    "get_transaction_id": get_transaction_id,
    "get_due_date": get_due_date,
}

TOOL_DESCRIPTIONS = {
    "get_s4_invoice": "Resolve a supplier invoice ID to its S/4 invoice ID.",
    "get_payment_status": "Get payment status for an S/4 invoice ID.",
    "get_transaction_id": "Get transaction details for an S/4 invoice ID.",
    "get_due_date": "Get the due date for an S/4 invoice ID.",
}

"""Payment investigation tool contracts with deterministic local fixtures.

Replace the fixture-backed implementations with the approved S/4 or Ariba API
calls when those API contracts and credentials are available. Keep these public
function names and response shapes stable for the agent.
"""

from typing import Any, Dict

from strands.tools import tool


_INVOICES = {
    "INV1234": {
        "supplier_invoice_id": "INV1234",
        "s4_invoice_id": "5100098765",
        "supplier_id": "SUP-1001",
    },
}
_PAYMENTS = {
    "5100098765": {
        "s4_invoice_id": "5100098765",
        "payment_status": "PAID",
        "transaction_id": "TX-900045",
    },
}
_DUE_DATES = {"5100098765": "2026-10-15"}


@tool(
    name="get_s4_invoice",
    description="Resolve a supplier invoice ID to its S/4 invoice ID.",
)
def get_s4_invoice(supplier_invoice_id: str) -> Dict[str, Any]:
    """Resolve a supplier invoice number to its S/4 invoice record."""
    if not supplier_invoice_id or not supplier_invoice_id.strip():
        raise ValueError("supplier_invoice_id must not be empty")
    result = _INVOICES.get(supplier_invoice_id.strip())
    if result is None:
        return {"supplier_invoice_id": supplier_invoice_id, "found": False}
    return {**result, "found": True}


@tool(
    name="get_payment_status",
    description="Get payment status for an S/4 invoice ID.",
)
def get_payment_status(s4_invoice_id: str) -> Dict[str, Any]:
    """Return payment status for an S/4 invoice ID."""
    if not s4_invoice_id or not s4_invoice_id.strip():
        raise ValueError("s4_invoice_id must not be empty")
    result = _PAYMENTS.get(s4_invoice_id.strip())
    if result is None:
        return {"s4_invoice_id": s4_invoice_id, "found": False}
    return {**result, "found": True}


@tool(
    name="get_transaction_id",
    description="Get transaction details for an S/4 invoice ID.",
)
def get_transaction_id(s4_invoice_id: str) -> Dict[str, Any]:
    """Return transaction details for an S/4 invoice ID."""
    payment = get_payment_status(s4_invoice_id)
    if not payment["found"]:
        return {"s4_invoice_id": s4_invoice_id, "found": False}
    return {
        "s4_invoice_id": s4_invoice_id,
        "transaction_id": payment.get("transaction_id"),
        "found": True,
    }


@tool(
    name="get_due_date",
    description="Get the due date for an S/4 invoice ID.",
)
def get_due_date(s4_invoice_id: str) -> Dict[str, Any]:
    """Return the due date for an S/4 invoice ID."""
    if not s4_invoice_id or not s4_invoice_id.strip():
        raise ValueError("s4_invoice_id must not be empty")
    due_date = _DUE_DATES.get(s4_invoice_id.strip())
    if due_date is None:
        return {"s4_invoice_id": s4_invoice_id, "found": False}
    return {"s4_invoice_id": s4_invoice_id, "due_date": due_date, "found": True}

import pytest

from task2_payment_agent.agents.payment_agent.tools import (
    get_due_date,
    get_payment_status,
    get_s4_invoice,
    get_transaction_id,
)


def test_payment_investigation_tool_sequence_uses_returned_invoice_id():
    invoice = get_s4_invoice("INV1234")
    assert invoice["s4_invoice_id"] == "5100098765"
    assert get_payment_status(invoice["s4_invoice_id"])["payment_status"] == "PAID"
    assert get_transaction_id(invoice["s4_invoice_id"])["transaction_id"] == "TX-900045"
    assert get_due_date(invoice["s4_invoice_id"])["due_date"] == "2026-10-15"


def test_unknown_invoice_returns_not_found_without_inventing_data():
    assert get_s4_invoice("UNKNOWN")["found"] is False
    assert get_payment_status("UNKNOWN")["found"] is False
    assert get_transaction_id("UNKNOWN")["found"] is False
    assert get_due_date("UNKNOWN")["found"] is False


def test_empty_identifier_is_rejected():
    with pytest.raises(ValueError):
        get_s4_invoice(" ")

"""MCP server exposing the local payment tool implementations."""

from task2_payment_agent.payment_mcp.tool_registry import TOOLS, TOOL_DESCRIPTIONS


def create_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP SDK is not installed. Install requirements-agent.txt first."
        ) from exc

    server = FastMCP("payment-investigation-tools")

    @server.tool(description=TOOL_DESCRIPTIONS["get_s4_invoice"])
    def get_s4_invoice(supplier_invoice_id: str) -> dict:
        return TOOLS["get_s4_invoice"](supplier_invoice_id)

    @server.tool(description=TOOL_DESCRIPTIONS["get_payment_status"])
    def get_payment_status(s4_invoice_id: str) -> dict:
        return TOOLS["get_payment_status"](s4_invoice_id)

    @server.tool(description=TOOL_DESCRIPTIONS["get_transaction_id"])
    def get_transaction_id(s4_invoice_id: str) -> dict:
        return TOOLS["get_transaction_id"](s4_invoice_id)

    @server.tool(description=TOOL_DESCRIPTIONS["get_due_date"])
    def get_due_date(s4_invoice_id: str) -> dict:
        return TOOLS["get_due_date"](s4_invoice_id)

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()

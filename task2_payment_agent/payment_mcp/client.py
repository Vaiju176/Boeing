"""Small synchronous MCP stdio client for exercising the local MCP server."""

from contextlib import AsyncExitStack
from typing import Any, Dict


class PaymentMCPClient:
    def __init__(self, server_module: str = "task2_payment_agent.payment_mcp.server"):
        self.server_module = server_module
        self._stack = AsyncExitStack()
        self._client = None
        self._session = None

    async def __aenter__(self):
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError as exc:
            raise RuntimeError(
                "MCP SDK is not installed. Install requirements-agent.txt first."
            ) from exc

        import sys

        params = StdioServerParameters(
            command=sys.executable, args=["-m", self.server_module]
        )
        self._client = await self._stack.enter_async_context(stdio_client(params))
        read_stream, write_stream = self._client
        self._session = await self._stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        await self._stack.aclose()

    async def list_tools(self):
        if self._session is None:
            raise RuntimeError("Use PaymentMCPClient as an async context manager")
        return await self._session.list_tools()

    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        if self._session is None:
            raise RuntimeError("Use PaymentMCPClient as an async context manager")
        return await self._session.call_tool(name, arguments)

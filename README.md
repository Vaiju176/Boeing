# Boeing Payment Investigation Prototype

This repository contains two separate workstreams. Each has its own source,
fixtures, tests, and run instructions.

```text
Boeing/
├── stage1_email_ingestion/   # Stage 1 mailbox ingestion prototype
│   ├── handler.py
│   ├── models.py
│   ├── mock_mailbox.json
│   ├── repositories/
│   ├── services/
│   ├── runtime/              # Local generated state
│   └── tests/
├── task2_payment_agent/      # Task 2 Strands + MCP prototype
│   ├── agents/payment_agent/
│   ├── payment_mcp/
│   ├── requirements-agent.txt
│   └── tests/
├── pyproject.toml
└── requirements-dev.txt
```

## Stage 1: Email ingestion

This is a local prototype using a Graph-like JSON mailbox, JSON persistence,
and a mock Step Functions handoff. It is not connected to Microsoft Graph or
AWS services.

From the repository root:

```bash
python -m stage1_email_ingestion.handler
```

Generated local state is written to `stage1_email_ingestion/runtime/`.

## Task 2: Payment investigation agent

This prototype uses Strands with deterministic mock payment tools and provides
an MCP server exposing those tools. It is not connected to S/4, Ariba, AWS, or
AgentCore yet.

Install the Task 2 dependencies:

```bash
python -m pip install -r task2_payment_agent/requirements-agent.txt
```

Run the agent from the repository root:

```bash
python -m task2_payment_agent.agents.payment_agent.agent
```

Run the MCP server over stdio:

```bash
python -m task2_payment_agent.payment_mcp.server
```

The `payment_mcp` directory name avoids shadowing the official Python `mcp`
SDK. The local fixtures are in `task2_payment_agent/agents/payment_agent/tools.py`;
replace their implementations with approved API calls when S/4 or Ariba
contracts are available. AgentCore deployment is a later step.

## Tests

Install pytest if needed, then run both workstreams' tests from the repository
root:

```bash
python -m pytest
```

# Task 2: Payment investigation agent

This Task 2 app is a small Strands-based agent that uses deterministic mock payment tools to investigate supplier invoice issues.

## Local run

From the repository root:

```bash
python3 -m pip install -r task2_payment_agent/requirements-agent.txt
python3 -m task2_payment_agent.agents.payment_agent.agent
```

## MCP server

```bash
python3 -m task2_payment_agent.payment_mcp.server
```

## AWS AgentCore deployment model

This project is designed to keep the same tool contract and agent logic while changing only the runtime packaging and AWS configuration.

### Runtime contract

- Keep the business logic in `task2_payment_agent/agents/payment_agent/*.py`
- Keep the mock tool names and response shapes as-is
- Package the app as a container and deploy it using AWS CLI + AgentCore

### Deployment notes

- The agent uses Strands + Bedrock in the runtime
- Bedrock access must be enabled and verified in the target AWS account
- The app may be run with environment variables such as:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=global.anthropic.claude-sonnet-4-6
```

## Important

The mock tool layer is intentionally simple and deterministic. Replace only the tool implementations when you have the real S/4 or Ariba API contract available.

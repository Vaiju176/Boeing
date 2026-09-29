FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AWS_REGION=us-east-1 \
    BEDROCK_MODEL_ID=global.anthropic.claude-sonnet-4-6

COPY requirements-dev.txt ./requirements-dev.txt
COPY task2_payment_agent/requirements-agent.txt ./task2_payment_agent/requirements-agent.txt
COPY pyproject.toml ./pyproject.toml

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-dev.txt \
    && python -m pip install -r task2_payment_agent/requirements-agent.txt \
    && python -m pip install 'botocore[crt]'

COPY . /app

CMD ["python", "-m", "task2_payment_agent.agentcore_runtime"]

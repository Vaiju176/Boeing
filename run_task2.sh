#!/bin/zsh
set -e

cd "$(dirname "$0")"

python3 -m pip install -r task2_payment_agent/requirements-agent.txt
python3 -m pip install 'botocore[crt]'

if ! command -v aws >/dev/null 2>&1; then
  echo "AWS CLI is not installed. Install it first: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
  exit 1
fi

echo "Checking AWS login..."
aws sts get-caller-identity >/dev/null

echo "Running Task 2 agent..."
python3 -m task2_payment_agent.agents.payment_agent.agent

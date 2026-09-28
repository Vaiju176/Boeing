# Stage 1: Email Ingestion

A small, local Python project that models an email-ingestion stage backed by a
Microsoft Graph-like mailbox and a mock Step Functions handoff. It uses only
the Python standard library at runtime.

## Architecture

```text
mock_mailbox.json
       |
       v
MockGraphRepository ---> IngestionService ---> EmailRepository
                                |                    |
                                v                    v
                       MockStepFunctionService   emails.json
                                |                    |
                                v                    v
                         executions.json     CheckpointRepository
                                                   |
                                                   v
                                             checkpoint.json
```

- **Repositories** isolate JSON-backed mailbox, email, execution, and checkpoint
  persistence from application logic.
- **Services** coordinate ingestion and simulate starting a Step Functions
  execution for each message.
- **Idempotency** is keyed by `message_id`. Re-reading a message does not create
  another stored email or mock execution.
- **Checkpointing** advances only after email persistence and handoff succeed.
  If an operation fails, the next run can retry the uncheckpointed message.
- JSON files are written atomically using a temporary file and `os.replace`.

The mock Graph repository uses an integer offset as a simple delta-sync token.
This models incremental synchronization for the fixed, append-only local
mailbox; it is not a replacement for Microsoft Graph delta links.

## Project layout

```text
stage1_email_ingestion/
├── .gitignore
├── pyproject.toml
├── requirements-dev.txt
├── handler.py
├── mock_mailbox.json
├── models.py
├── repositories/
│   ├── __init__.py
│   ├── checkpoint_repository.py
│   ├── email_repository.py
│   ├── json_file.py
│   ├── mock_graph_repository.py
│   └── step_function_repository.py
├── services/
│   ├── __init__.py
│   ├── ingestion_service.py
│   └── step_function_service.py
└── tests/
    ├── conftest.py
    ├── test_handler.py
    ├── test_ingestion_service.py
    └── test_repositories.py
```

## Run

Run one ingestion batch from the project directory:

```bash
python handler.py
```

The first run stores the two sample emails and records two mock executions.
Later runs report no new messages unless the mailbox is appended. Runtime state
is written to `runtime/`.

The handler can also be called as a Lambda-style entry point:

```python
from handler import lambda_handler

result = lambda_handler({"batch_size": 10}, None)
```

An event may optionally provide `mailbox_path` and `runtime_dir` to use
alternate local files.

## Test

Install pytest if it is not already available, then run:

```bash
python -m pytest
```

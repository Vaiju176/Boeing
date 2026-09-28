import json

import pytest

from handler import build_ingestion_service


@pytest.fixture
def mailbox_path(tmp_path):
    path = tmp_path / "mock_mailbox.json"
    path.write_text(
        json.dumps(
            [
                {
                    "message_id": "MSG-001",
                    "subject": "First",
                    "sender": "one@example.com",
                    "received_at": "2026-09-28T08:00:00Z",
                    "body": "First message",
                },
                {
                    "message_id": "MSG-002",
                    "subject": "Second",
                    "sender": "two@example.com",
                    "received_at": "2026-09-28T08:15:00Z",
                    "body": "Second message",
                },
            ]
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def ingestion_service(mailbox_path, tmp_path):
    return build_ingestion_service(mailbox_path, tmp_path / "runtime")

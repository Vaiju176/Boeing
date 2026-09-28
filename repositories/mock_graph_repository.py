import json
from pathlib import Path
from typing import List

from models import EmailMessage


class MockGraphRepository:
    """Reads a local mailbox and exposes offset-based Graph-like sync."""

    def __init__(self, mailbox_path: Path):
        self.mailbox_path = Path(mailbox_path)

    def list_messages(self, start_index: int, limit: int) -> List[EmailMessage]:
        if start_index < 0:
            raise ValueError("start_index must be non-negative")
        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        with self.mailbox_path.open("r", encoding="utf-8") as stream:
            raw_messages = json.load(stream)
        if not isinstance(raw_messages, list):
            raise ValueError("Mock mailbox must contain a JSON array")
        return [
            EmailMessage.from_dict(item)
            for item in raw_messages[start_index : start_index + limit]
        ]

from pathlib import Path
from typing import Dict, List

from models import EmailMessage
from repositories.json_file import JsonFile


class EmailRepository:
    def __init__(self, path: Path):
        self._file = JsonFile(path)

    def save_if_absent(self, message: EmailMessage) -> bool:
        records = self._read_records()
        if any(record["message_id"] == message.message_id for record in records):
            return False
        records.append(message.to_dict())
        self._file.write(records)
        return True

    def get_by_message_id(self, message_id: str) -> Dict[str, str]:
        for record in self._read_records():
            if record["message_id"] == message_id:
                return record
        raise KeyError(message_id)

    def list_all(self) -> List[Dict[str, str]]:
        return self._read_records()

    def _read_records(self) -> List[Dict[str, str]]:
        records = self._file.read([])
        if not isinstance(records, list):
            raise ValueError("Persisted emails must contain a JSON array")
        return records

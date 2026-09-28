from pathlib import Path
from typing import Dict, List

from repositories.json_file import JsonFile


class StepFunctionRepository:
    """Stores mock Step Functions executions, unique by source message."""

    def __init__(self, path: Path):
        self._file = JsonFile(path)

    def record_execution_if_absent(self, message_id: str) -> bool:
        executions = self.list_all()
        if any(execution["message_id"] == message_id for execution in executions):
            return False
        executions.append(
            {
                "message_id": message_id,
                "status": "STARTED",
                "state_machine": "mock-email-processor",
            }
        )
        self._file.write(executions)
        return True

    def list_all(self) -> List[Dict[str, str]]:
        executions = self._file.read([])
        if not isinstance(executions, list):
            raise ValueError("Persisted executions must contain a JSON array")
        return executions

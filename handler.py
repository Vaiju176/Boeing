import json
from pathlib import Path
from typing import Any, Dict, Optional

from repositories.checkpoint_repository import CheckpointRepository
from repositories.email_repository import EmailRepository
from repositories.mock_graph_repository import MockGraphRepository
from repositories.step_function_repository import StepFunctionRepository
from services.ingestion_service import IngestionService
from services.step_function_service import MockStepFunctionService


PROJECT_DIR = Path(__file__).resolve().parent


def build_ingestion_service(
    mailbox_path: Optional[Path] = None,
    runtime_dir: Optional[Path] = None,
) -> IngestionService:
    mailbox = Path(mailbox_path) if mailbox_path else PROJECT_DIR / "mock_mailbox.json"
    runtime = Path(runtime_dir) if runtime_dir else PROJECT_DIR / "runtime"
    return IngestionService(
        graph_repository=MockGraphRepository(mailbox),
        email_repository=EmailRepository(runtime / "emails.json"),
        checkpoint_repository=CheckpointRepository(runtime / "checkpoint.json"),
        step_function_service=MockStepFunctionService(
            StepFunctionRepository(runtime / "executions.json")
        ),
    )


def lambda_handler(event: Optional[Dict[str, Any]] = None, context: Any = None) -> Dict[str, Any]:
    if event is None:
        event = {}
    if not isinstance(event, dict):
        raise TypeError("event must be a dictionary")
    mailbox_path = event.get("mailbox_path")
    runtime_dir = event.get("runtime_dir")
    batch_size = event.get("batch_size", 100)
    if isinstance(batch_size, bool) or not isinstance(batch_size, int):
        raise ValueError("batch_size must be an integer")

    result = build_ingestion_service(mailbox_path, runtime_dir).sync(batch_size)
    return {"statusCode": 200, "body": result}


if __name__ == "__main__":
    print(json.dumps(lambda_handler(), indent=2))

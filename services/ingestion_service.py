from typing import Any, Dict

from repositories.checkpoint_repository import CheckpointRepository
from repositories.email_repository import EmailRepository
from repositories.mock_graph_repository import MockGraphRepository
from services.step_function_service import MockStepFunctionService


class IngestionService:
    def __init__(
        self,
        graph_repository: MockGraphRepository,
        email_repository: EmailRepository,
        checkpoint_repository: CheckpointRepository,
        step_function_service: MockStepFunctionService,
    ):
        self._graph_repository = graph_repository
        self._email_repository = email_repository
        self._checkpoint_repository = checkpoint_repository
        self._step_function_service = step_function_service

    def sync(self, batch_size: int = 100) -> Dict[str, Any]:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        checkpoint = self._checkpoint_repository.get_checkpoint()
        messages = self._graph_repository.list_messages(checkpoint, batch_size)
        persisted = 0
        already_persisted = 0
        handoffs_started = 0

        for message in messages:
            if self._email_repository.save_if_absent(message):
                persisted += 1
            else:
                already_persisted += 1

            if self._step_function_service.start_execution(message.message_id):
                handoffs_started += 1

            checkpoint += 1
            self._checkpoint_repository.set_checkpoint(checkpoint)

        return {
            "fetched": len(messages),
            "persisted": persisted,
            "already_persisted": already_persisted,
            "handoffs_started": handoffs_started,
            "checkpoint": checkpoint,
        }

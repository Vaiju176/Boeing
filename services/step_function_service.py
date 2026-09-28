from repositories.step_function_repository import StepFunctionRepository


class MockStepFunctionService:
    def __init__(self, repository: StepFunctionRepository):
        self._repository = repository

    def start_execution(self, message_id: str) -> bool:
        """Return True only when a new mock execution is recorded."""
        return self._repository.record_execution_if_absent(message_id)

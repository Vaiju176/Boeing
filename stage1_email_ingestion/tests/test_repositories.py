from stage1_email_ingestion.models import EmailMessage
from stage1_email_ingestion.repositories.email_repository import EmailRepository
from stage1_email_ingestion.repositories.step_function_repository import StepFunctionRepository
from stage1_email_ingestion.services.step_function_service import MockStepFunctionService


def test_email_persistence_is_idempotent_by_message_id(tmp_path):
    repository = EmailRepository(tmp_path / "emails.json")
    original = EmailMessage(
        message_id="MSG-001",
        subject="Original",
        sender="sender@example.com",
        received_at="2026-09-28T08:00:00Z",
        body="Original message",
    )
    duplicate = EmailMessage(
        message_id="MSG-001",
        subject="Changed",
        sender="sender@example.com",
        received_at="2026-09-28T08:00:00Z",
        body="Changed message",
    )

    assert repository.save_if_absent(original) is True
    assert repository.save_if_absent(duplicate) is False
    assert repository.list_all() == [original.to_dict()]


def test_mock_step_function_handoff_is_idempotent(tmp_path):
    service = MockStepFunctionService(
        StepFunctionRepository(tmp_path / "executions.json")
    )

    assert service.start_execution("MSG-001") is True
    assert service.start_execution("MSG-001") is False

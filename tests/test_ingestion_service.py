import json

import pytest

from repositories.checkpoint_repository import CheckpointRepository


def test_sync_persists_messages_handoffs_and_checkpoint(ingestion_service, tmp_path):
    result = ingestion_service.sync()
    runtime = tmp_path / "runtime"

    assert result == {
        "fetched": 2,
        "persisted": 2,
        "already_persisted": 0,
        "handoffs_started": 2,
        "checkpoint": 2,
    }
    assert [email["message_id"] for email in json.loads(
        (runtime / "emails.json").read_text(encoding="utf-8")
    )] == ["MSG-001", "MSG-002"]
    assert [execution["message_id"] for execution in json.loads(
        (runtime / "executions.json").read_text(encoding="utf-8")
    )] == ["MSG-001", "MSG-002"]
    assert json.loads((runtime / "checkpoint.json").read_text(encoding="utf-8")) == {
        "last_processed_index": 2
    }


def test_sync_is_idempotent(ingestion_service):
    ingestion_service.sync()
    second_result = ingestion_service.sync()

    assert second_result == {
        "fetched": 0,
        "persisted": 0,
        "already_persisted": 0,
        "handoffs_started": 0,
        "checkpoint": 2,
    }


def test_sync_respects_batch_size_and_resumes(ingestion_service):
    first_result = ingestion_service.sync(batch_size=1)
    second_result = ingestion_service.sync(batch_size=1)

    assert first_result["checkpoint"] == 1
    assert first_result["persisted"] == 1
    assert second_result["checkpoint"] == 2
    assert second_result["persisted"] == 1


def test_checkpoint_cannot_move_backwards(tmp_path):
    repository = CheckpointRepository(tmp_path / "checkpoint.json")
    repository.set_checkpoint(2)

    with pytest.raises(ValueError, match="cannot move backwards"):
        repository.set_checkpoint(1)


def test_invalid_batch_size_is_rejected(ingestion_service):
    with pytest.raises(ValueError, match="batch_size"):
        ingestion_service.sync(batch_size=0)

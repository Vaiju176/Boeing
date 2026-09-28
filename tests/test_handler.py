import pytest

from handler import lambda_handler


def test_handler_accepts_paths_from_event(mailbox_path, tmp_path):
    result = lambda_handler(
        {
            "mailbox_path": str(mailbox_path),
            "runtime_dir": str(tmp_path / "runtime"),
            "batch_size": 1,
        }
    )

    assert result["statusCode"] == 200
    assert result["body"]["fetched"] == 1
    assert result["body"]["checkpoint"] == 1


def test_handler_rejects_non_dictionary_event():
    with pytest.raises(TypeError, match="event must be a dictionary"):
        lambda_handler([])

from pathlib import Path

from repositories.json_file import JsonFile


class CheckpointRepository:
    def __init__(self, path: Path):
        self._file = JsonFile(path)

    def get_checkpoint(self) -> int:
        state = self._file.read({"last_processed_index": 0})
        if not isinstance(state, dict):
            raise ValueError("Checkpoint state must contain a JSON object")
        checkpoint = state.get("last_processed_index")
        if not isinstance(checkpoint, int) or checkpoint < 0:
            raise ValueError("last_processed_index must be a non-negative integer")
        return checkpoint

    def set_checkpoint(self, index: int) -> None:
        if not isinstance(index, int) or index < 0:
            raise ValueError("checkpoint must be a non-negative integer")
        current = self.get_checkpoint()
        if index < current:
            raise ValueError("checkpoint cannot move backwards")
        self._file.write({"last_processed_index": index})

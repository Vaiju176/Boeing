import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JsonFile:
    """Small helper for reading and atomically replacing JSON documents."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def read(self, default: Any) -> Any:
        if not self.path.exists():
            return default
        with self.path.open("r", encoding="utf-8") as stream:
            return json.load(stream)

    def write(self, value: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(self.path.parent),
                prefix=self.path.name + ".",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_path = Path(stream.name)
                json.dump(value, stream, indent=2)
                stream.write("\n")
            os.replace(str(temporary_path), str(self.path))
        except Exception:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
            raise

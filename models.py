from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class EmailMessage:
    message_id: str
    subject: str
    sender: str
    received_at: str
    body: str

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "EmailMessage":
        required_fields = ("message_id", "subject", "sender", "received_at", "body")
        missing = [field for field in required_fields if not isinstance(value.get(field), str)]
        if missing:
            raise ValueError(
                "Email message fields must be strings; missing or invalid: "
                + ", ".join(missing)
            )
        if not value["message_id"]:
            raise ValueError("message_id must not be empty")
        return cls(**{field: value[field] for field in required_fields})

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)

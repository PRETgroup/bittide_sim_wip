from dataclasses import dataclass

@dataclass
class BittideFrame:
    sender_timestamp: int
    sender_phys_time: float
    signals: list[str]
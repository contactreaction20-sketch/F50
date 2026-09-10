"""Autonomy levels for FUTURE-50."""

from enum import Enum


class AutonomyLevel(Enum):
    """Configurable autonomy for user-controlled execution."""

    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5

    @classmethod
    def from_string(cls, value: str) -> "AutonomyLevel":
        key = value.lower().replace("level_", "level_").strip()
        normalized = key.replace("-", "_").replace(" ", "_")
        for item in cls:
            if item.name.lower() == normalized:
                return item
        try:
            return cls(int(normalized.split("level_")[-1]))
        except Exception:
            return cls.LEVEL_2

    @property
    def name(self) -> str:
        return self._name_

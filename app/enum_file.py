from enum import Enum as PyEnum

class StatusEnum(PyEnum):
    ACTIVE = "исправен"
    BROKEN = "сломался"
    WRITTEN_OFF = "списан"
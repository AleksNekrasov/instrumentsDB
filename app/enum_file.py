from enum import Enum as PyEnum

class StatusEnum(PyEnum):
    WRITTEN_OFF = "Списан"       # Списан
    IN_WORK = "в работе"         # В работе
    IN_STOCK = "на складе"       # На складе
    IN_REPAIR = "в ремонте"      # В ремонте
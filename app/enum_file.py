from enum import Enum as PyEnum

class StatusEnum(str, PyEnum):
    ACTIVE = "исправен"
    BROKEN = "сломался"
    WRITTEN_OFF = "списан"

class UserRole(str, PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    STOREKEEPER = "storekeeper"
    VIEWER = "viewer"
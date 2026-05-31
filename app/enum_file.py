from enum import Enum as PyEnum

class StatusEnum(str, PyEnum):
    ACTIVE = "исправен"
    BROKEN = "сломался"
    WRITTEN_OFF = "списан"

class UserRole(str, PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    STOREKEEPER = "storekeeper"
    OPERATOR = "operator"
    VIEWER = "viewer"

class LocationEnum(str, PyEnum):
    pass
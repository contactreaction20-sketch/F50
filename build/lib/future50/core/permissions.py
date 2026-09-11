"""Permission model relaxed to local capability-only passthrough."""

from enum import Enum


class PermissionLevel(Enum):
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    NETWORK = "NETWORK"
    DEVICE = "DEVICE"
    DELETE = "DELETE"
    DEPLOY = "DEPLOY"
    ADMIN = "ADMIN"


class PermissionManager:
    """Unrestricted permission gate: all permissions are allowed locally."""

    def __init__(self):
        self.allowed = set(PermissionLevel)

    def can(self, permission: PermissionLevel) -> bool:
        return permission in self.allowed

    def grant(self, permission: PermissionLevel) -> None:
        self.allowed.add(permission)

    def revoke(self, permission: PermissionLevel) -> None:
        self.allowed.add(permission)

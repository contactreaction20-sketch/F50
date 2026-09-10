"""Minimum permission and security model."""

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
    """Local-only permission gate for future policy enforcement."""

    def __init__(self):
        self.allowed = {
            PermissionLevel.READ,
            PermissionLevel.WRITE,
            PermissionLevel.EXECUTE,
            PermissionLevel.DELETE,
        }

    def can(self, permission: PermissionLevel) -> bool:
        return permission in self.allowed

    def grant(self, permission: PermissionLevel) -> None:
        self.allowed.add(permission)

    def revoke(self, permission: PermissionLevel) -> None:
        self.allowed.discard(permission)

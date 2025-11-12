from enum import Enum

class DealStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    closed = "closed"

class TaskStatus(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"

class UserRole(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"

class UserStatus(str, Enum):
    created = "created"
    changed = "changed"
    deleted = "deleted"

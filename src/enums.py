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

class ActionStatus(str, Enum):
    created = "created"
    changed = "changed"
    deleted = "deleted"
    error = "error"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class DateColumn(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    closed_at = "closed_at"

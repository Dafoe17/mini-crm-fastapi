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
    admin = "admin"
    manager = "manager"
    user = "user"

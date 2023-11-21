from enum import StrEnum


class Role(StrEnum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


class Priority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGRENT"


class State(StrEnum):
    BACKLOG = "Backlog"
    TODO = "To do"
    INPROGRESS = "In Progress"
    REVIEW = "In Review"
    QA = "QA"
    DONE = "Done"


class Label(StrEnum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"
    QA = "qa"
    DESIGN = "design"
    OTHER = "other"

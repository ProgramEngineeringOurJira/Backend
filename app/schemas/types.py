from enum import StrEnum


class Role(StrEnum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    GUEST = "GUEST"


def states():
    return ["Backlog", "To do", "In Progress", "In Review", "QA", "Done"]


class Priority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGRENT"

from enum import Enum


class ProjectType(Enum):
    BACK_END = 'BAE'
    FRONT_END = 'FRE'
    IOS = 'IOS'
    ANDROID = 'AND'

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.title()) for item in cls]


class IssuePriority(Enum):
    LOW = 'LOW'
    MEDIUM = 'MED'
    HIGH = 'HIGH'

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.title()) for item in cls]


class IssueTag(Enum):
    BUG = 'BUG'
    FEATURE = 'FEAT'
    TASK = 'TASK'

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.title()) for item in cls]


class CustomStatus(Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'INPR'
    FINISHED = 'FINI'

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name.title()) for item in cls]

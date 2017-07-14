from enum import Enum, unique


@unique
class Support(Enum):
    UNKNOWN = "unknown"
    NO = "no"
    YES = "yes"

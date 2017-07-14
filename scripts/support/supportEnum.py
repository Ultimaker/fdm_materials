from enum import Enum, unique


@unique
class Support(Enum):
    """
    Defines different kinds of support.
    """

    UNKNOWN = "unknown"
    NO = "no"
    YES = "yes"

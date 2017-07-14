from enum import Enum, unique

"""
Defines different kinds of support.
"""
@unique
class Support(Enum):
    UNKNOWN = "unknown"
    NO = "no"
    YES = "yes"

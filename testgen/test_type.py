from enum import Enum


class TestType(str, Enum):
    COLLATION_SHORT = "collation_short"
    LANG_NAMES = "lang_names"
    LIKELY_SUBTAGS = "likely_subtags"
    MESSAGE_FMT2 = "message_fmt2"
    NUMBER_FMT = "number_fmt"


test_types = [t.value for t in TestType]

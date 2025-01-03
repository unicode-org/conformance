from enum import Enum


class TestType(str, Enum):
    COLLATION_SHORT = "collation_short"
    DATETIME_FMT = "datetime_fmt"
    LANG_NAMES = "lang_names"
    LIKELY_SUBTAGS = "likely_subtags"
    LIST_FMT = "list_fmt"
    MESSAGE_FMT2 = "message_fmt2"
    NUMBER_FMT = "number_fmt"
    PLURAL_RULES = "plural_rules"
    RELATIVE_DATETIME_FMT = "rdt_fmt"


test_types = [t.value for t in TestType]

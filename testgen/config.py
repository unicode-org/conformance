from os import getcwd
from os.path import exists, join

_unified_cli_paths = {
    "logging_config": "logging.conf",
    "default_input": join("DDT_DATA", "testData"),
}

_legacy_paths = {key: join("..", value) for key, value in _unified_cli_paths.items()}

using_unified_cli = exists(join(getcwd(), "conformance"))

paths = _unified_cli_paths if using_unified_cli else _legacy_paths

#!/bin/bash
set -e

# Tests node with coll_short_shift and number_fmt
python3 verifier.py --file_base ../DDT_DATA --exec node --test_type collation_short number_fmt lang_names likely_subtags

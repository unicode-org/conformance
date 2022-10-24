# Tests nodejs with coll_short_shift and number_fmt
python3 verifier.py --file_base ~/ICU_conformance/conformance/DDT_DATA --exec nodejs --test_type coll_shift_short number_fmt lang_names --verify_file_name coll_verify_shift.json num_fmt_verify_file.json lang_name_verify_file.json

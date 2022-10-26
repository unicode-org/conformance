# Tests rust with coll_short_shift and number_fmt
python3 verifier.py --file_base ../DDT_DATA --exec rust --test_type coll_shift_short number_fmt --verify_file_name coll_verify_shift.json num_fmt_verify_file.json

# Runs collation test on only on nodejs
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py --test coll_shift_short number_fmt lang_names --exec nodejs --file_base ../DDT_DATA

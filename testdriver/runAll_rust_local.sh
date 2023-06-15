# Runs collation test on only on rust
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py  --icu_version icu71 --test coll_shift_short number_fmt --exec rust --file_base ../DDT_DATA

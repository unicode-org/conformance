# Runs collation test on only on rust
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py --test coll_shift_short --exec rust --run_limit 27 --file_base ~/DDT_DATA --debug 3

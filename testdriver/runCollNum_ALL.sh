# Runs collation test on only on all executors
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py --test coll_shift_short number_fmt --exec node rust "python3 ../executors/python/executor.py" --run_limit 27 --file_base ~/DDT_DATA

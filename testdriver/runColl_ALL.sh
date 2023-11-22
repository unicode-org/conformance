# Runs collation test on node, rust, and python
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py --test coll_shift_short --exec node rust "python3 ../executors/python/executor.py" --run_limit 27 --file_base ~/DDT_DATA

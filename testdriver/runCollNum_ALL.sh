# Runs collation test on only on nodejs
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py --test coll_shift_short number_fmt --exec nodejs rust "python ../executors/python/executor.py" --run_limit 27 --file_base ~/DDT_DATA

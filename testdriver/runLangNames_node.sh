# Runs collation test on only on nodejs
# Test data and output directories are under ~/DDT_DATA
python3 testdriver.py --test lang_names --exec nodejs --run_limit 27 --file_base ~/DDT_DATA

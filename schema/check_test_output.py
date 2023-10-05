# Run schema validation on all test outputs for all tests.

# For ICU Conformance project, Data Driven Testing
import argparse
from datetime import datetime
import glob
import json


import logging
import os.path
import sys

import schema
import schema_files
from schema_files import schema_file_map
from schema_files import all_test_types

def main(args):
    if len(args) <= 1:
        logging.error('Please specify the path to the test output directory')
        exit(1)
    else:
        test_output_path = args[1]

    print('TEST OUTPUT PATH = %s' % test_output_path)

    logger = logging.Logger("Checking Test Data vs. Schemas LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Test Generated test data vs. schemas  files')

    # TODO: get ICU versions
    executor_set = set()
    icu_version_set = set()
    test_type_set = set()
    if os.path.exists(test_output_path):
        executor_path = os.path.join(test_output_path, '*')
        executor_paths = glob.glob(executor_path)
        for path in executor_paths:
            if os.path.isdir(path):
                executor_set.add(os.path.basename(path))

        icu_path = os.path.join(test_output_path, '*', 'icu*')
        icu_dirs = glob.glob(icu_path)

        test_output_json_path = os.path.join(test_output_path, '*', 'icu*', '*.json')
        json_files = glob.glob(test_output_json_path)

        for file in json_files:
            try:
                test_file_prefix = os.path.splitext(os.path.basename(file))[0]
                test_type = schema_files.test_file_to_test_type_map[test_file_prefix]
                test_type_set.add(test_type)
            except BaseException as err:
                logging.error('!!! %s for file %s', err, file
                              )
        for dir in icu_dirs:
            icu_version_set.add(os.path.basename(dir))

    icu_versions = sorted(list(icu_version_set))
    print('ICU directories = %s' % icu_versions)
    print('test types = %s' % all_test_types)

    schema_validator = schema.conformance_schema_validator()
    # Todo: use setters to initialize schema_validator
    schema_validator.schema_base = '.'
    schema_validator.test_output_base = test_output_path
    schema_validator.test_data_base = None
    schema_validator.icu_versions = icu_versions
    schema_validator.test_types = list(test_type_set)
    schema_validator.executors = list(executor_set)
    schema_validator.debug = 1
    schema_base = '.'
    schema_data_results = []
    schema_count = 0

    all_results = schema_validator.validate_test_output_with_schema()
    print('  %d results for generated test data' % (len(all_results)))

    schema_errors = 0
    failed_validations = []
    passed_validations = []
    schema_count = len(all_results)
    for result in all_results:
        print(result)
        if result[2]:
            passed_validations.append(result)
        else:
            failed_validations.append(result)

    # Create .json
    summary_json = {
        'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
        'validations': {
            'failed': failed_validations,
            'passed': passed_validations
        }
    }

    summary_data = json.dumps(summary_json)

    try:
        output_filename = os.path.join(test_output_path, 'test_output_validation_summary.json')
        file_out = open(output_filename, mode='w', encoding='utf-8')
        file_out.write(summary_data)
        file_out.close()
    except BaseException as error:
        logging.warning('Error: %s. Cannot save validation summary in file %s', err, output_filename)


    if schema_errors:
        print('Test data file files: %d fail out of %d:' % (
            len(schema_errors, schema_count)))
        for failure in schema_errors:
            print('  %s' % failure)
        exit(1)
    else:
        print("All %d test output files match with schema" % schema_count)
        exit(0)

if __name__ == "__main__":
    main(sys.argv)

# TODO: Implement this!

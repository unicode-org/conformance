# Run schema validation on all test outputs for all tests.

# For ICU Conformance project, Data Driven Testing
import argparse
from datetime import datetime
import glob
import json


import logging
import logging.config
import os.path
import sys

import schema_validator
import schema_files
from schema_files import SCHEMA_FILE_MAP
from schema_files import ALL_TEST_TYPES

def main(args):
    logging.config.fileConfig("../logging.conf")

    if len(args) <= 1:
        logging.error('Please specify the path to the test output directory')
        exit(1)
    else:
        test_output_path = args[1]

    logging.debug('TEST OUTPUT PATH = %s', test_output_path)

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
                test_type = schema_files.TEST_FILE_TO_TEST_TYPE_MAP[test_file_prefix]
                test_type_set.add(test_type)
            except BaseException as err:
                logging.debug('No file (%s) during schema check output: %s', file, err
                              )
        for dir in icu_dirs:
            icu_version_set.add(os.path.basename(dir))

    icu_versions = sorted(list(icu_version_set))
    logging.debug('ICU directories = %s', icu_versions)
    logging.debug('test types = %s', ALL_TEST_TYPES)

    validator = schema_validator.ConformanceSchemaValidator()
    # Todo: use setters to initialize validator
    validator.schema_base = '.'
    validator.test_output_base = test_output_path
    validator.test_data_base = None
    validator.icu_versions = icu_versions
    validator.test_types = list(test_type_set)
    validator.executors = list(executor_set)
    validator.debug = 1
    schema_base = '.'
    schema_data_results = []
    schema_count = 0

    all_results = validator.validate_test_output_with_schema()
    logging.info('  %d results for test output', len(all_results))

    schema_errors = 0
    failed_validations = []
    passed_validations = []
    schema_count = len(all_results)
    for result in all_results:
        logging.debug(result)
        if result['result']:
            passed_validations.append(result)
        else:
            failed_validations.append(result)

    # Create .json
    try:
        summary_json = {
            'validation_type': 'output of test executors',
            'description': 'Validation of test execution outputs vs. schema',
            'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
            'validations': {
                'failed': failed_validations,
                'passed': passed_validations
            }
        }
    except BaseException as error:
        summary_json = {}

    # Create outputs from these results.
    try:
        summary_data = json.dumps(summary_json)
    except TypeError as err :
        logging.error('Error: %s\n  Cannot dump JSON for %s: ',
                      err, summary_json)
    try:
        output_filename = os.path.join(test_output_path, 'test_output_validation_summary.json')
        file_out = open(output_filename, mode='w', encoding='utf-8')
        file_out.write(summary_data)
        file_out.close()
    except BaseException as error:
        logging.warning('Error: %s. Cannot save validation summary in file %s', error, output_filename)


    if schema_errors:
        logging.error('Test data file files: %d fail out of %d:', 
            len(schema_errors, schema_count))
        for failure in schema_errors:
            logging.error('  %s', failure)
        exit(1)
    else:
        logging.info("All %d test output files match with schema", schema_count)
        exit(0)

if __name__ == "__main__":
    main(sys.argv)

# TODO: Implement this!

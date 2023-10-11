# Checks test data generated against schema in Conformance Testing
# For ICU Conformance project, Data Driven Testing
import argparse
from datetime import datetime
import glob
import json


import logging
import os.path
import sys

import schema_validator
import schema_files
from schema_files import SCHEMA_FILE_MAP
from schema_files import ALL_TEST_TYPES

def main(args):
    if len(args) <= 1:
        logging.error('Please specify the path to test data directory')
        return
    else:
        test_data_path = args[1]

    print('TEST DATA PATH = %s' % test_data_path)

    logger = logging.Logger("Checking Test Data vs. Schemas LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Test Generated test data vs. schemas  files')

    # TODO: get ICU versions
    icu_versions = []
    test_type_set = set()
    if os.path.exists(test_data_path):
        check_path = os.path.join(test_data_path, 'icu*')
        icu_dirs = glob.glob(check_path)
        print('ICU DIRECTORIES = %s' % icu_dirs)
        for dir in icu_dirs:
            icu_versions.append(os.path.basename(dir))

    print('ICU directories = %s' % icu_versions)
    print('test types = %s' % ALL_TEST_TYPES)

    validator = schema_validator.ConformanceSchemaValidator()
    # Todo: use setters to initialize validator
    validator.schema_base = '.'
    validator.test_data_base = test_data_path
    validator.icu_versions = sorted(icu_versions)
    validator.test_types = ALL_TEST_TYPES
    validator.debug = 1
    schema_base = '.'
    schema_data_results = []
    schema_count = 0

    all_results = validator.validate_test_data_with_schema()
    print('  %d results for generated test data' % (len(all_results)))

    schema_errors = 0
    failed_validations = []
    passed_validations = []
    schema_count = len(all_results)
    for result in all_results:
        print(result)
        if result['result']:
            passed_validations.append(result)
        else:
            failed_validations.append(result)

    # Create .json
    summary_json = {
        'validation_type': 'Generated test data files',
        'description': 'Results of validating generated test data agains schema',
        'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
        'validations': {
            'failed': failed_validations,
            'passed': passed_validations
        }
    }

    summary_data = json.dumps(summary_json)

    try:
        output_filename = os.path.join(test_data_path, 'test_data_validation_summary.json')
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
        print("All %d generated test data files match with schema" % schema_count)
        exit(0)

if __name__ == "__main__":
    main(sys.argv)

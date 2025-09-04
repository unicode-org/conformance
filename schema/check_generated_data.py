# Checks test data generated against schema in Conformance Testing
# For ICU Conformance project, Data Driven Testing

from datetime import datetime
import glob
import json

from jsonschema import Draft7Validator, ValidationError

import argparse
import logging
import logging.config
import os.path
import sys

import schema_validator
from schema_files import ALL_TEST_TYPES


def main(args):
    logging.config.fileConfig("../logging.conf")

    arg_parser = argparse.ArgumentParser(description='Schema check arguments')
    arg_parser.add_argument('schema_base', help='Where to find the files to validate')
    arg_parser.add_argument(
        '--run_serial', action='store_true',
        help='Set to process serially. Parallel is the default.')

    schema_options = arg_parser.parse_args(args[2:])

    if len(args) <= 1:
        logging.error('Please specify the path to test data directory')
        return
    else:
        test_data_path = schema_options.schema_base

    logging.debug('TEST DATA PATH = %s', test_data_path)

    logger = logging.Logger("Checking Test Data vs. Schemas LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Test Generated test data vs. schemas  files')

    # TODO: get ICU versions
    icu_versions = []
    if os.path.exists(test_data_path):
        check_path = os.path.join(test_data_path, 'icu*')
        icu_dirs = glob.glob(check_path)
        for dir_name in icu_dirs:
            icu_versions.append(os.path.basename(dir_name))

    logging.debug('ICU directories = %s', icu_versions)
    logging.debug('test types = %s', ALL_TEST_TYPES)

    validator = schema_validator.ConformanceSchemaValidator()

    validator.run_serial = schema_options.run_serial

    # Todo: use setters to initialize validator
    validator.schema_base = '.'
    validator.test_data_base = test_data_path
    validator.icu_versions = sorted(icu_versions)
    validator.test_types = ALL_TEST_TYPES
    validator.debug = 1

    all_results = validator.validate_test_data_with_schema()
    logging.info('  %d results for generated test data', len(all_results))

    schema_errors = []
    failed_validations = []
    passed_validations = []
    schema_count = len(all_results)
    for result in all_results:
        if result['result']:
            passed_validations.append(result)
        else:
            failed_validations.append(result)

    # Create .json
    summary_json = {
        'validation_type': 'Generated test data files',
        'description': 'Results of validating generated test data against schema',
        'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
        'validations': {
            'failed': failed_validations,
            'passed': passed_validations
        }
    }

    try:
        summary_data = json.dumps(summary_json)
    except BaseException as error:
        logging.error('json.dumps Summary data problem: %s at %s', error, error)
        sys.exit(1)

    output_filename = os.path.join(test_data_path, 'test_data_validation_summary.json')
    try:
        file_out = open(output_filename, mode='w', encoding='utf-8')
        file_out.write(summary_data)
        file_out.close()
    except BaseException as error:
        schema_errors.append(output_filename)
        logging.fatal('Error: %s. Cannot save validation summary in file %s', error, output_filename)
        sys.exit(1)

    if schema_errors:
        logging.critical('Test data file files: %d fail out of %d:',
                         len(schema_errors), schema_count)
        for failure in schema_errors:
            logging.critical('  %s', failure)
        sys.exit(1)
    else:
        logging.info("All %d generated test data files match with schema", schema_count)


if __name__ == "__main__":
    main(sys.argv)

# Run schema validation on all test outputs for all tests.

# For ICU Conformance project, Data Driven Testing
from datetime import datetime
import glob
import json

import logging
import logging.config
import os.path
import sys

import schema_validator
import schema_files
from schema_files import ALL_TEST_TYPES


def main(args):
    logging.config.fileConfig("../logging.conf")

    if len(args) <= 1:
        logging.error('Please specify the path to the test output directory')
        exit(1)
    else:
        test_output_path = args[1]


    logger = logging.Logger("Checking Test Data vs. Schemas LOGGER")
    logger.setLevel(logging.INFO)

    logger.debug('TEST OUTPUT PATH = %s', test_output_path)

    logger.info('+++ Test Generated test data vs. schemas  files')

    # TODO: get ICU versions
    executor_set = set()
    icu_version_set = set()
    test_type_set = set()
    json_files = []
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
            test_file_prefix = os.path.splitext(os.path.basename(file))[0]
            try:
                test_type = schema_files.TEST_FILE_TO_TEST_TYPE_MAP[test_file_prefix]
                test_type_set.add(test_type)
            except BaseException as err:
                logger.debug('No file (%s) during schema check output: %s', file, err
                              )
        for dir_nane in icu_dirs:
            icu_version_set.add(os.path.basename(dir_nane))

    icu_versions = sorted(list(icu_version_set))
    logger.debug('ICU directories = %s', icu_versions)
    logger.debug('test types = %s', ALL_TEST_TYPES)

    validator = schema_validator.ConformanceSchemaValidator()
    # Todo: use setters to initialize validator
    validator.schema_base = '.'
    validator.test_output_base = test_output_path
    validator.test_data_base = None
    validator.icu_versions = icu_versions
    validator.test_types = list(test_type_set)
    validator.executors = list(executor_set)
    validator.debug = 1

    all_results, test_validation_plans = validator.validate_test_output_with_schema()
    logger.info('  %d results for test output', len(all_results))

    # Check if any files in the expected list were not validated.
    test_paths = set()
    for plan in test_validation_plans:
        test_paths.add(plan['test_result_file'])

    for json_file in json_files:
        if json_file not in test_paths:
            logger.fatal('JSON file %s was not verified against a schema', json_file)
            # Bail out right away!
            exit(1)

    failed_validations = []
    passed_validations = []
    schema_count = len(all_results)
    for result in all_results:
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
        logger.fatal('Cannot create summary_json %s', error)
        exit(1)

    # Create outputs from these results.
    try:
        summary_data = json.dumps(summary_json)
    except TypeError as err:
        logger.fatal('Error: %s\n  Cannot dump JSON for %s', err, summary_json)
        exit(1)

    output_filename = os.path.join(test_output_path, 'test_output_validation_summary.json')
    try:
        file_out = open(output_filename, mode='w', encoding='utf-8')
        file_out.write(summary_data)
        file_out.close()
    except BaseException as error:
        logger.fatal('Error: %s. Cannot save validation summary in file %s', error, output_filename)
        # Don't continue after this problem.
        exit(1)

    logger.info("All %d test output files match with schema", schema_count)
    return


if __name__ == "__main__":
    main(sys.argv)

# TODO: Implement this!

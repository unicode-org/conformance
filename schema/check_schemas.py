# Schema checker for the schemas in Conformance Testing
# For ICU Conformance project, Data Driven Testing

from datetime import datetime
import glob
import json

import logging
import logging.config
from multiprocessing.dummy import Pool
import multiprocessing
import os.path
import sys

import schema_validator
from schema_files import ALL_TEST_TYPES


class ValidateSchema:
    def __init__(self, schema_base='.'):
        self.schema_base = schema_base
        logging.config.fileConfig("../logging.conf")

    def save_schema_validation_summary(self, validation_status):

        failed_validations = []
        passed_validations = []
        for result in validation_status:
            if result['result']:
                passed_validations.append(result)
            else:
                failed_validations.append(result)

        summary_json = {
            'validation_type': 'Schema files',
            'description': 'Results of checking schema files for correct syntax',
            'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
            'schema_validation_base': self.schema_base,
            'validations': {
                'failed': failed_validations,
                'passed': passed_validations
            }
        }

        try:
            summary_data = json.dumps(summary_json)
        except BaseException as err:
            logging.error('%s: Cannot create JSON summary: %s', err, summary_json)
            return None

        output_filename = os.path.join(self.schema_base, 'schema_validation_summary.json')
        try:
            file_out = open(output_filename, mode='w', encoding='utf-8')
            file_out.write(summary_data)
            file_out.close()
        except BaseException as error:
            logging.warning('Error: %s. Cannot save validation summary in file %s', error, output_filename)
            return None

        return output_filename


def parallel_validate_schema(validator, file_names):
    num_processors = multiprocessing.cpu_count()
    logging.info('Schema validation: %s processors for %s schema validations', num_processors, len(file_names))

    processor_pool = multiprocessing.Pool(num_processors)
    # How to get all the results
    result = None
    try:
        result = processor_pool.map(validator.validate_schema_file, file_names)
    except multiprocessing.pool.MaybeEncodingError as error:
        pass
    return result


def main(args):
    logger = logging.Logger("TEST SCHEMAS LOGGER")
    logger.setLevel(logging.WARNING)
    logger.info('+++ Test JSON Schema files')

    validator = schema_validator.ConformanceSchemaValidator()
    # Todo: use setters to initialize validator
    validator.schema_base = '.'

    if len(args) > 1:
        schema_base = args[1]
    else:
        schema_base = '.'
    schema_errors = []
    schema_count = 0

    val_schema = ValidateSchema(schema_base)

    # An array of information to be reported on the main DDT page
    validation_status = []
    schema_file_paths = []
    for test_type in ALL_TEST_TYPES:
        schema_test_base = os.path.join(schema_base, test_type)
        schema_test_json_files = os.path.join(schema_test_base, '*.json')
        schema_file_names = glob.glob(schema_test_json_files)
        schema_file_paths.extend(schema_file_names)

    results = parallel_validate_schema(validator, schema_file_paths)
    if not results:
        # This should stop the whole thing!
        exit(1)

    for outcome in results:
        result, err, file_path, test_type = outcome[0], outcome[1], outcome[2], outcome[3]
        schema_file = os.path.basename(file_path)
        validation_status.append({"test_type": test_type,
                                  "schema_path": file_path,
                                  "result": result,
                                  "error_info": str(err)
                                  })
        if not result:
            schema_errors.append([schema_file, result, err, file_path])
            logging.error('Bad Schema at %s', schema_file)
        schema_count += 1

    output_filename = val_schema.save_schema_validation_summary(validation_status)

    if schema_errors:
        logging.error('SCHEMA: %d fail out of %d:', 
                      len(schema_errors), schema_count)
        for failure in schema_errors:
            logging.error('  %s', failure)
        # We need to clobber the process
        sys.exit(1)
    else:
        logging.info("All %d schema are valid in file %s", schema_count, output_filename)
        exit(0)


# Add validation results to test data with validation.
if __name__ == "__main__":
    main(sys.argv)

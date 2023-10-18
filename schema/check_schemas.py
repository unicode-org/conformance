# Schema checker for the schemas in Conformance Testing
# For ICU Conformance project, Data Driven Testing
import argparse
from datetime import datetime
import glob
import json


import logging
import os.path
import sys

import schema_validator
from schema_files import ALL_TEST_TYPES

class ValidateSchema():
    def __init__(self, schema_base='.'):
        self.schema_base = schema_base

    def save_schema_validation_summary(self, validation_status):

        failed_validations = []
        passed_validations = []
        for result in validation_status:
            print(result)
            if result['result']:
                passed_validations.append(result)
            else:
                failed_validations.append(result)

        summary_json = {
            'validation_type': 'Schema files',
            'description': 'Results of checking schema files for correct syntax',
            'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
            'schema_validation_base': self.schema_base,
            'when_processed': datetime.now().strftime('%Y-%m-%d T%H%M%S.%f'),
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

        try:
            output_filename = os.path.join(self.schema_base, 'schema_validation_summary.json')
            file_out = open(output_filename, mode='w', encoding='utf-8')
            file_out.write(summary_data)
            file_out.close()
        except BaseException as error:
            logging.warning('Error: %s. Cannot save validation summary in file %s', err, output_filename)
            return None

        return output_filename

def main(args):
    logger = logging.Logger("TEST SCHEMAS LOGGER")
    logger.setLevel(logging.INFO)
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

    for test_type in ALL_TEST_TYPES:
        schema_test_base = os.path.join(schema_base, test_type)
        schema_test_json_files = os.path.join(schema_test_base, '*.json')
        schema_file_names = glob.glob(schema_test_json_files)
        for schema_file in schema_file_names:
            result, err, file_path = validator.validate_schema_file(schema_file)
            validation_status.append({"test_type": test_type,
                                      "schema_path": schema_file,
                                      "result": result,
                                      "error_info": str(err)
                                      })
            if not result:
                schema_errors.append([schema_file, result, err, file_path])
                logging.error('Bad Schema at %s', schema_file)
            schema_count += 1

    ok = val_schema.save_schema_validation_summary(validation_status)

    if schema_errors:
        print('SCHEMA: %d fail out of %d:' % (
            len(schema_errors), schema_count))
        for failure in schema_errors:
            print('  %s' % failure)
        exit(1)
    else:
        print("All %d schema are valid" % schema_count)
        exit(0)


    # TODO: Add validation results to test data with validation.
if __name__ == "__main__":
    main(sys.argv)

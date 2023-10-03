# Schema checker for the schemas in Conformance Testing
# For ICU Conformance project, Data Driven Testing
import argparse
import glob
import json


import logging
import os.path
import sys

import schema
import schema_files
from schema_files import schema_file_map

def main(args):
    logger = logging.Logger("TEST SCHEMAS LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Test JSON Schema files')

    schema_validator = schema.conformance_schema_validator()
    # Todo: use setters to initialize schema_validator
    schema_validator.schema_base = '.'

    schema_base = '.'
    schema_errors = []
    schema_count = 0

    # An array of information to be reported on the main DDT page
    validation_status = []

    for test_type in schema_files.all_test_types:
        for schema_name in ['test_schema.json', 'result_schema.json']:
            schema_file_path = os.path.join(schema_base, test_type, schema_name)
            result, err = schema_validator.validate_schema_file(schema_file_path)
            validation_status.append({"test_type": test_type,
                                      "schema_path": schema_file_path,
                                      "result": result,
                                      "error_info": err
                                      })
            if not result:
                schema_errors.append([schema_file_path, result, err])
                logging.error('Bad Schema at %s', schema_file_path)
            schema_count += 1

    if schema_errors:
        print('SCHEMA: %d fail out of %d:' % (
            len(schema_errors), schema_count))
        for failure in schema_errors:
            print('  %s' % failure)
        exit(1)
    else:
        print("All %d schema files are valid" % schema_count)
        exit(0)


    # TODO: Add validation results to test data with validation.
if __name__ == "__main__":
    main(sys.argv)

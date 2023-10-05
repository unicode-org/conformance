# Schema handling for test data, verification data, results files, etc.
# For ICU Conformance project, Data Driven Testing
import argparse
import glob
import json

import jsonschema.exceptions
from jsonschema import validate
from jsonschema import ValidationError
from jsonschema import exceptions

import logging
import os.path
import sys

import schema_files
from schema_files import schema_file_map

# ?? Move to the initialization
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Given a directory, validate JSON files against expected schema

class conformance_schema_validator():
    def __init__(self):
        # Where to find these files
        self.schema_base = None
        self.test_data_base = None
        self.test_output_base = None
        self.test_types = schema_files.all_test_types
        self.executors = []
        self.icu_versions = []
        self.debug_leve = 0

    def validate_json_file(self, schema_file_path, data_file_path):
        # Returns  True, None if data is validated against the schema
        # returns  Falee, error_string if there's a problem
        try:
            schema_file = open(schema_file_path, encoding='utf-8', mode='r')
        except FileNotFoundError as err:
            return_error = err
            logging.error('  Cannot open data file %s.\n   Err = %s', schema_file_path, err)
            return False, err

        try:
            data_file = open(data_file_path, encoding='utf-8', mode='r')
        except FileNotFoundError as err:
            logging.error('  Cannot open data file %s.\n   Err = %s', data_file_path, err)
            return_error = err
            return False, err

      # Get the schema file and validate the data against it
        try:
            schema = json.load(schema_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON schema: %s', schema_file_path)
            logging.error('  Error is %s', err)
            return False, err

        try:
            data_to_check = json.load(data_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON data: %s', ddata_file_path)
            logging.error('  Error is %s', err)
            return False, err

        # Now check this!
        try:
            validate(data_to_check, schema)
            logging.info('This test output file validates: %s, %s:',
                         data_file_path, schema_file_path)
            return True, None
        except ValidationError as err:
            logging.error('ValidationError for test output %s and schema %s',
                          data_file_path, schema_file_path )
            logging.error('  Error = %s', err)
            return False, err
        except exceptions.SchemaError as err:
            logging.error('SchemaError: Cannot validate with test output %s and schema %s. ',
                          data_file_path, schema_file_path)
            logging.error('  Error = %s', err)
            return False, err
        except BaseException as err:
            logging.error('Another failure: %s', err)
            return False, err

    def validate_test_data_with_schema(self):
        all_results = []
        for test_type in self.test_types:
            for icu_version in self.icu_versions:
                if self.debug > 0:
                    logging.debug('Checking test data %s, %s', test_type, icu_version)
                logging.info('Checking %s, %s', test_type, icu_version)
                results, msg = self.check_test_data_schema(icu_version, test_type)
                if results == 'no file':
                    # This is not an error but simple a test that wasn't run.
                    continue
                if not results:
                    logging.warning('VALIDATION FAILS: %s %s. MSG=%s', test_type, icu_version, msg)
                else:
                    logging.warning('VALIDATION WORKS: %s %s', test_type, icu_version)
                all_results.append([test_type, icu_version, results, msg])
        return all_results

    def check_test_data_schema(self, icu_version, test_type):
        # Check the generated test data for structure agains the schema
        logging.info('Validating %s with icu version %s', test_type, icu_version)

        # Check test output vs. the test data schema
        schema_verify_file = os.path.join( self.schema_base, test_type, 'test_schema.json')
        if not os.path.exists(schema_verify_file):
            return 'no file', "no schema file"

        filename_map = schema_file_map[test_type]
        result_file_name = schema_file_map[test_type]['test_data']['prod_file']
        test_data_file = os.path.join(self.test_data_base, icu_version, result_file_name)
        if not os.path.exists(test_data_file):
            return 'no file', "no data file"

        result, err_info = self.validate_json_file(schema_verify_file, test_data_file)

        if result:
            logging.info('Test data %s validated with %s, ICU %s', test_type, icu_version)
        else:
            logging.error('Test data %s FAILED with ICU %s: %s', test_type, icu_version, err_info)

        return result, err_info

    def check_test_output_schema(self, icu_version, test_type, executor):
        # Check the output of the tests for structure against the schema
        logging.info('Validating %s with icu version %s', test_type, icu_version)

        # Check test output vs. the schema
        schema_file_name = schema_file_map[test_type]['result_data']['schema_file']
        schema_verify_file = os.path.join(self.schema_base, schema_file_name)
        if not os.path.exists(schema_verify_file):
            return 'no file', "no schema file"
        result_file_name = schema_file_map[test_type]['result_data']['prod_file']
        test_result_file = os.path.join(self.test_output_base, executor, icu_version, result_file_name)
        if not os.path.exists(test_result_file):
            return 'no file', "no data file"

        result, err_msg = self.validate_json_file(schema_verify_file, test_result_file)

        if result:
            logging.info('Result data %s validated with %s, ICU %s', test_type, executor, icu_version)
        else:
            logging.error('Result data %s FAILED with %s ICU %s: %s', test_type, executor, icu_version, err_msg)

        return result, err_msg
    def validate_schema_file(self, schema_file_path):
        try:
            schema_file = open(schema_file_path, encoding='utf-8', mode='r')
        except FileNotFoundError as err:
            return_error = err
            logging.error('  Cannot open data file %s.\n   Err = %s', schema_file_path, err)
            return False, err

        # Get the schema file and validate the data against it
        try:
            schema = json.load(schema_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON schema: %s', schema_file_path)
            logging.error('  Error is %s', err)
            return False, err

        try:
            validate(None, schema)
        except jsonschema.exceptions.SchemaError as err:
            return False, err
        except jsonschema.exceptions.ValidationError as err:
            # This is OK since it's only checking the schema's structure
            return True, None

        return True, None

    def check_schema_files(self, schema_file_base='.'):
        # First, check all the schema files for correct formatting.
        schema_errors = []
        schema_count = 0
        for test_type in self.test_types:
            for schema_name in ['test_schema.json', 'result_schema.json']:
                schema_count += 1
                schema_file_path = os.path.join(self.schema_base, test_type, schema_name)
                result, err = self.validate_schema_file(schema_file_path)
                if not result:
                    schema_errors.append([schema_file_path, result, err])
                    logging.error('Bad Schema at %s', schema_file_path)

        if schema_errors:
            logging.warning('SCHEMA failures: %s' % schema_errors)
        else:
            logging.info("All %d schema files are valid!", schema_count)

        return schema_errors

    def validate_test_output_with_schema(self):
        all_results = []
        for executor in self.executors:
            for icu_version in self.icu_versions:
                for test_type in self.test_types:
                    logging.info('Checking %s, %s, %s', test_type, icu_version, executor)
                    results, msg = self.check_test_output_schema(icu_version, test_type, executor)
                    if results == 'no file':
                        # This is not an error but simple a test that wasn't run.
                        continue
                    if not results:
                        logging.warning('VALIDATION FAILS: %s %s %s. MSG=%s', test_type, icu_version, executor, msg)
                    else:
                        logging.warning('VALIDATION WORKS: %s %s %s', test_type, icu_version, executor)
                    all_results.append([test_type, icu_version, executor, results, msg])
        return all_results

def set_up_args():
    parser = argparse.ArgumentParser(prog='schema')
    parse.add_argument('--schema_base_folder', nargs=1, default='.')
    parse.add_argument('--test_data_folder', nargs=1, default='.')
    parse.add_argument('--test_output_folder', nargs=1, default='.')
    parse.add_argument('--icu_versions', nargs='*', default='ALL')
    parse.add_argument('--test_types', nargs='*', default='ALL')
    parse.add_argument('--executors', nargs='*', default='ALL')
    new_args = parse.parse(args)
    return new_args

def process_args(args):
    # Args:
    #   Base directory for icu test data or ALL
    #   Test types (or ALL)
    #   Directory for test result files
    # Get name of test and type
    if len(args) < 2:
        print('you gotta give me something...')
        return

    base_folder = args[1]
    base_folders = []  #
    if os.path.basename(base_folder) == "ALL":
        # TODO: Get all the subdirectories
        dir_name = os.path.dirname(base_folder)
        base_folders = glob.glob(dir_name + '/icu*')
    else:
        base_folders = [base_folder]

    test_type = None
    test_types = []
    if len(args) > 2:
        # Test types
        test_type = args[2]
        if test_type == "ALL":
            test_types = schema_files.all_test_types
        else:
            test_types = [test_type]

    result_folders = []
    if len(args) > 3:
        result_base = args[3]
        if os.path.basename(result_base) == "ALL":
            dir_name = os.path.dirname(result_base)
            result_folders = glob.glob(dir_name + '/*/icu*')
        else:
            result_folders = [result_base]
    else:
        result_base = None
    return base_folders, test_types, result_folders

def main(args):
    # Args:
    #   Base directory for icu test data or ALL
    #   Test types (or ALL)
    #   Directory for test result files
    # Get name of test and type
    if len(args) < 2:
        logging.warning('you gotta give me something...')
        return

    # new_args = set_up_args()

    # TODO: fix command line args
    base_folders, test_types, result_folders = process_args(args)

    logger = logging.Logger("TEST_GENERATE LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Running JSON Schema tests')

    schema_validator = conformance_schema_validator()
    # Todo: use setters to initialize schema_validator
    schema_validator.schema_base = '.'
    schema_validator.test_data_base = os.path.split(base_folders[0])[0]
    schema_validator.test_output_base =  os.path.split(os.path.split(result_folders[0])[0])[0]
    schema_validator.icu_versions = ['icu71', 'icu72', 'icu73', 'icu74']
    schema_validator.executors = ['node', 'rust', 'dart_web']

    print('Checking test outputs')
    all_test_out_results = schema_validator.validate_test_output_with_schema()
    for result in all_test_out_results:
        print('  %s' % result)

    # Check all schema files for correctness.
    schema_errors = schema_validator.check_schema_files()
    if schema_errors:
        logging.error('INVALID SCHEMA: %s', schema_errors)
    else:
        logging.info('All schemas are valid: %s', schema_errors)

    icu_versions = ['icu71', 'icu72', 'icu73', 'icu74']
    executor_list = ['node', 'rust', 'dart_web']

    print('Checking generated data')
    all_test_data_results = schema_validator.validate_test_data_with_schema()
    for result in all_test_data_results:

        print('  %s' % result)

    print('Checking test outputs')
    all_test_out_results = schema_validator.validate_test_output_with_schema()
    for result in all_test_out_results:
        print('  %s' % result)
    return

if __name__ == "__main__":
    main(sys.argv)

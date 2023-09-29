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
class ddt_validate():
    def __init__(self, base_folders=None):
        self.test_data_folders = []
        self.valid_folder = False
        if base_folders:
            self.set_folders(base_folders)
        self.result_paths = []

        self.schema_folder = '.'

    def set_folders(self, base_folders):
        self.test_data_folders =  base_folders
        # Folder typically contains an icu version, e.g., 'icu73'
        self.folder = base_folders

    def set_result_paths(self, path_list):
        self.result_paths = path_list

    def general_paths(self, test_type, category, base_path):
        # Get the schema file paths for the given test
        # Uses the current folder
        base_path = self.folder

        if not test_type in schema_file_map:
            return None
        info = schema_file_map[test_type]

        return {
            'test_data':
                os.path.join(self.folder, info['test_data'][category]),
            'verify_data':
                os.path.join(self.folder, info['verify_data'][category]),
            'result_data':
                os.path.join(self.folder, info['result_data'][category])
            }

    def schema_paths(self, test_type):
        category = 'schema_file'
        if not test_type in schema_file_map:
            return None

        info = schema_file_map[test_type]
        return {
            'test_data':
                os.path.join(self.schema_folder, info['test_data'][category]),
            'verify_data':
                os.path.join(self.schema_folder, info['verify_data'][category]),
            'result_data':
                os.path.join(self.schema_folder, info['result_data'][category])
        }
        return self.general_paths(test_type, 'schema_file', '')

    def test_data_paths(self, test_type):
        base_path = self.folder

        return self.general_paths(test_type, 'prod_file', base_path)

    def validate_json_test_files(self, test_type, data_type):
        # Get the data and the corresponding schema file.

        # Read both files and validate

        return

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

    def validate_json_structure(self, test_type, data_paths, schema_paths, data_type):

        # Data type: one of 'test_data', verify_data', result_data" indicating which to verify
        # Get the data and the corresponding schema file.
        json_schema_path = schema_paths[data_type]
        json_file_to_check = data_paths[data_type]
        result, error_msg = validate_json_file(json_schema_path, json_file_to_check)

    def validate_json_schema_file(self, schema_file_path):
        # TODO: Fill this in
        return

def process_args(args, validator):
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

def check_simple_test_data(icu_version, test_type):
    print('TEST DATA: Validating %s with icu version %s', test_type, icu_version)
    validator = ddt_validate()
    schema_base = '/usr/local/google/home/ccornelius/ICU_conformance/conformance/schema'
    data_base = '/usr/local/google/home/ccornelius/ICU_conformance/conformance/TEMP_DATA/'

    # Check the schema for test data
    schema_file = os.path.join(schema_base, test_type, 'test_schema.json')
    test_data_file = os.path.join(data_base, 'testData', icu_version, 'collation_test.json')

    if not os.path.exists(schema_file):
        return 'no file', "no schema file"
    if not os.path.exists(test_data_file):
        return 'no file', "no data file"

    r1, err_msg1 = validator.validate_json_file(schema_file, test_data_file)

    if r1:
        logging.info('Test data %s validated with %s ICU %s', test_type, icu_version)
    else:
        logging.error('Test data %s FAILED with %s ICU %s: %s', test_data_file, test_type, icu_version, err_msg1)
    return r1, err_msg1

def check_test_output_schema(icu_version, test_type, executor):
    logging.info('Validating %s with icu version %s', test_type, icu_version)
    validator = ddt_validate()
    schema_base = '/usr/local/google/home/ccornelius/ICU_conformance/conformance/schema'
    data_base = '/usr/local/google/home/ccornelius/ICU_conformance/conformance/TEMP_DATA/'

    # Check test output vs. the schema
    schema_verify_file = os.path.join(schema_base, test_type, 'result_schema.json')
    if not os.path.exists(schema_verify_file):
        return 'no file', "no schema file"
    result_file_name = schema_file_map[test_type]['result_data']['prod_file']
    test_result_file = os.path.join(data_base, 'testOutput', executor, icu_version, result_file_name)
    if not os.path.exists(test_result_file):
        return 'no file', "no data file"

    r2, err_msg2 = validator.validate_json_file(schema_verify_file, test_result_file)

    if r2:
        logging.info('Result data %s validated with %s, ICU %s', test_type, executor, icu_version)
    else:
        logging.error('Result data %s FAILED with %s ICU %s: %s', test_type, executor, icu_version, err_msg2)

    return r2, err_msg2

def validate_schema_file(schema_file_path):
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
        return True, err

    return True, None

def set_up_args():
    parser = argparse.ArgumentParser(prog='schema')
    parse.add_argument('--schema_base_folder', nargs=1, default='.')
    parse.add_argument('--test_data_folder', nargs=1, default='.')
    parse.add_argument('--icu_versions', nargs='*', default='ALL')
    parse.add_argument('--test_types', nargs='*', default='ALL')
    new_args = parse.parse(args)
    return new_args

def main(args):
    # Args:
    #   Base directory for icu test data or ALL
    #   Test types (or ALL)
    #   Directory for test result files
    # Get name of test and type
    if len(args) < 2:
        print('you gotta give me something...')
        return

    # new_args = set_up_args()

    # TODO:
    validator = ddt_validate()

    base_folders, test_types, result_folders = process_args(args, validator)

    logger = logging.Logger("TEST_GENERATE LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Running JSON Schema tests')

    icu_versions = ['icu71', 'icu72', 'icu73', 'icu74']
    executor_list = ['node', 'rust', 'dart_web']

    # TODO: MOVE TO SEPARATE FUNCTION in a class
    # First, check all the schema files for correct formatting.
    schema_base = '/usr/local/google/home/ccornelius/ICU_conformance/conformance/schema'
    schema_errors = []
    for test_type in schema_files.all_test_types:
        for schema_name in ['test_schema.json', 'result_schema.json']:
            schema_file_path = os.path.join(schema_base, test_type, schema_name)
            result, err = validate_schema_file(schema_file_path)
            if not result:
                schema_errors.append([schema_file_path, result, err])
                logging.error('Bad Schema at %s', schema_file_path)

    if schema_errors:
        print('SCHEMA failures: %s' % schema_errors)
    else:
        print("All schema files are valid")


    all_results = []

    print()
    print('Output validation')
    for test_type in schema_files.all_test_types:
        for icu_version in icu_versions:
            for executor in executor_list:
                print(test_type, icu_version, executor)
                results, msg = check_test_output_schema(icu_version, test_type, executor)
                if results == 'no file':
                    continue
                if not results:
                    logging.warning('VALIDATION FAILS: %s %s %s. MSG=%s', test_type, icu_version, executor, msg)
                else:
                    logging.warning('VALIDATION WORKS: %s %s %s', test_type, icu_version, executor)
                all_results.append([test_type, icu_version, executor, results, msg])

    print(all_results)
    #TODO: Finish this
    return

    validator = ddt_validate()

    # Get all the platforms platforms = Set()
    platforms = set()
    for result in result_folders:
        path_split = os.path.split(result_folders)
        icu_result_path = path_split[-1]
        executor_split = os.path.split(path_split[0])
        platforms.add(executor_split[-1])

    validator.base_folders = base_folders
    validator.set_result_paths(result_folders)

    # TODO: Run for each test directory in base_folders

    for test_type in test_types:
        data_paths = validator.test_data_paths(test_type)
        schema_paths = validator.schema_paths(test_type)

        if not data_paths:
            print('No data_paths found for %s' % test_type)
            return

        logging.info(data_paths)
        logging.info(schema_paths)

    # TODO: Now, what should this do?
    #    validator.check_schema(test_type)

        json_date = data_paths
        data_type_list = ['test_data', 'result_data']  #   Add this later 'result_data']

        for data_type in data_type_list:
            is_valid, errorr_msg = validator.validate_json_structure(test_type, data_paths, schema_paths, data_type)

            if is_valid:
                logging.info('VALID: %s %s %s %s', test_type, data_paths, schema_paths, data_type)
            else:
                logging.error('!!! INVALID JSON: %s %s %s %s', test_type, data_paths, schema_paths, data_type)


if __name__ == "__main__":
    main(sys.argv)

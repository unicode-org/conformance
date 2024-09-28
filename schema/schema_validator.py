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
import logging.config
import multiprocessing as mp
import os.path
import sys

import schema_files
from schema_files import SCHEMA_FILE_MAP

# ?? Move to the initialization
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Given a directory, validate JSON files against expected schema


def parallel_validate_schema(validator, json_pairs):
        num_processors = mp.cpu_count()
        logging.info('JSON validation: %s processors for %s plans' % num_processors, len(file_names))

        # How to get all the results
        processor_pool = mp.Pool(num_processors)
        with processor_pool as p:
            result = p.map(validator.validate_schema_file, file_names)
        return result

class ConformanceSchemaValidator():
    def __init__(self):
        # Where to find these files
        self.schema_base = None
        self.test_data_base = None
        self.test_output_base = None
        self.test_types = schema_files.ALL_TEST_TYPES
        self.executors = []
        self.icu_versions = []
        self.debug_leve = 0

        logging.config.fileConfig("../logging.conf")

    def validate_json_file(self, schema_and_data_paths):
        schema_file_path = schema_and_data_paths['schema_verify_file']
        data_file_path = schema_and_data_paths['test_result_file']
        # Returns  True, None if data is validated against the schema
        # returns  False, error_string if there's a problem

        result_data = {
            'test_type': schema_and_data_paths['test_type'],
            'result': None,
            'schema_file': schema_file_path,
            'data_path': data_file_path,
            'error': None,
            'error_info': None
        }

        try:
            schema_file = open(schema_file_path, encoding='utf-8', mode='r')
        except FileNotFoundError as err:
            return_error = err
            logging.error('  Cannot open data file %s.\n   Err = %s', schema_file_path, err)
            result_data['result'] = False
            result_data['error'] = err
            return result_data

        try:
            data_file = open(data_file_path, encoding='utf-8', mode='r')
        except FileNotFoundError as err:
            logging.debug('  Cannot open data file %s.\n   Err = %s', data_file_path, err)

            result_data['result'] = False
            result_data['error'] = err
            return result_data

      # Get the schema file and validate the data against it
        try:
            schema = json.load(schema_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON schema: %s', schema_file_path)
            logging.error('  Error is %s', err)
            result_data['result'] = False
            result_data['error'] = err
            return result_data

        try:
            data_to_check = json.load(data_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON data: %s', ddata_file_path)
            logging.error('  Error is %s', err)
            result_data['result'] = False
            result_data['error'] = err
            return result_data
        # Now check this!
        try:
            validate(data_to_check, schema)
            # Everything worked!
            result_data['result'] = True
            result_data['error'] = None
            return result_data
        except ValidationError as err:
            logging.error('ValidationError for test output %s and schema %s',
                          data_file_path, schema_file_path )
            logging.error('  Error = %s', err)
            result_data['result'] = False
            result_data['error'] = err
            return result_data
        except exceptions.SchemaError as err:
            logging.error('SchemaError: Cannot validate with test output %s and schema %s. ',
                          data_file_path, schema_file_path)
            logging.error('  Error = %s', err)
            result_data['result'] = False
            result_data['error'] = err
            return result_data
        except BaseException as err:
            logging.error('Another failure: %s', err)
            result_data['result'] = False
            result_data['error'] = err
            return result_data

    def validate_test_data_with_schema(self):
        all_results = []
        schema_test_info = []

        # Check for all the possible files
        json_file_pattern = os.path.join(self.test_data_base, '*', '*.json')
        verify_pattern = os.path.join(self.test_data_base, '*', '*verify.json')
        json_verify_files_list = glob.glob(verify_pattern)
        json_files_list = glob.glob(json_file_pattern)
        json_test_list = []
        for file in json_files_list:
            if file not in json_verify_files_list:
                json_test_list.append(file)

        test_data_files_not_found = []
        for test_type in self.test_types:
            for icu_version in self.icu_versions:
                file_path_pair = self.get_schema_data_info(icu_version, test_type)
                if file_path_pair:
                    schema_test_info.append(file_path_pair)
                else:
                    test_data_files_not_found.append([icu_version, test_type])
                    logging.debug('No data test file  %s for %s, %s', file_path_pair, test_type, icu_version)
                    pass

        if test_data_files_not_found:
            logging.warning('%d test data not checked', len(test_data_files_not_found))

        results = self.parallel_check_test_data_schema(schema_test_info)

        for result_data in results:
            logging.debug('test result data = %s', result_data)
            msg = result_data['err_info']
            if not result_data['data_file_name']:
                # This is not an error but simple a test that wasn't run.
                continue
            if not result_data['result']:
                logging.warning('FAIL: Test data %s, %s. MSG=%s',
                                test_type, icu_version, result_data['err_info'])
            else:
                logging.debug('Test data validated: %s %s', result_data['test_type'], result_data['icu_version'])
            all_results.append(result_data)
        return all_results

    def parallel_check_test_data_schema(self, schema_test_data):
        num_processors = mp.cpu_count()
        logging.info('Schema validation: %s processors for %s schema/test data pairs',
                     num_processors,
                     len(schema_test_data))

        # Returns all the results
        processor_pool = mp.Pool(num_processors)
        with processor_pool as p:
            result = p.map(self.check_test_data_against_schema, schema_test_data)
        return result

    def get_schema_data_info(self, icu_version, test_type):
        # Gets pairs of schema and file names for test_type
        schema_verify_file = os.path.join(self.schema_base, test_type, 'test_schema.json')
        filename_map = SCHEMA_FILE_MAP[test_type]
        result_file_name = filename_map['test_data']['prod_file']
        test_file_name = os.path.join(self.test_data_base, icu_version, result_file_name)
        if os.path.exists(test_file_name):
            return {
                'test_type': test_type,
                'icu_version': icu_version,
                'schema_verify_file': schema_verify_file,
                'test_result_file': test_file_name
            }
        else:
            # logging.warning('## get_schema_data_info. No file at test_file_name: %s', test_file_name);
            return None

    def check_test_data_against_schema(self, schema_info):
        icu_version = schema_info['icu_version']
        test_type = schema_info['test_type']
        schema_verify_file = schema_info['schema_verify_file'],
        test_file_name = schema_info['test_result_file']
        results = {
            'test_type': test_type,
            'icu_version': icu_version,
            'result': None,
            'err_info': None,
            'test_schema': schema_verify_file,
            'data_file_name': test_file_name
        }
        result = self.validate_json_file(schema_info)

        if isinstance(result, list):
            results['error_message'] = result[0]
        else:
            results['error_info'] = result['error']

        results['result'] = result['result']

        return results

    def check_test_data_schema(self, icu_version, test_type):
        # Check the generated test data for structure agains the schema
        logging.debug('Validating %s with %s', test_type, icu_version)

        # Check test output vs. the test data schema
        schema_verify_file = os.path.join( self.schema_base, test_type, 'test_schema.json')
        results = {
            'test_type': test_type,
            'icu_version': icu_version,
            'result': None,
            'err_info': None,
            'test_schema': schema_verify_file,
            'data_file_name': None
        }
        if not os.path.exists(schema_verify_file):
            results['err_info'] = "No file"
            return Results

        filename_map = SCHEMA_FILE_MAP[test_type]
        result_file_name = SCHEMA_FILE_MAP[test_type]['test_data']['prod_file']
        test_file_name = os.path.join(self.test_data_base, icu_version, result_file_name)
        if not os.path.exists(test_file_name):
            return results

        results['data_file_name'] = test_file_name
        result, err_info = self.validate_json_file([schema_verify_file, test_file_name])
        if isinstance(result, list):
            results['error_message'] = result[0]
            test_result = False
        else:
            test_result = result
        results['result'] = result
        if result:
            logging.debug('Test data %s validated successfully, with ICU %s', test_type, icu_version)
        else:
            logging.error('Test data %s FAILED with ICU %s: %s', test_type, icu_version, err_info)

        return results

    def get_test_output_schema_plan(self, icu_version, test_type, executor):
        # Check the output of the tests for structure against the schema

        # Check test output vs. the schema
        schema_file_name = SCHEMA_FILE_MAP[test_type]['result_data']['schema_file']
        schema_verify_file = os.path.join(self.schema_base, schema_file_name)
        result_dir_path = os.path.join(self.test_output_base, executor, icu_version)
        if not os.path.exists(result_dir_path):
            return None

        result_file_name = SCHEMA_FILE_MAP[test_type]['result_data']['prod_file']
        test_result_file = os.path.join(result_dir_path, result_file_name)

        if not os.path.exists(test_result_file):
                return None

        return {
            'test_type': test_type,
            'icu_version': icu_version,
            'executor': executor, 'schema_verify_file': schema_verify_file,
            'test_result_file': test_result_file
        }

    def check_test_output_schema(self, icu_version, test_type, executor):
        # Check the output of the tests for structure against the schema
        logging.debug('Validating test output: %s %s %s', executor , test_type, icu_version)

        # Check test output vs. the schema
        schema_file_name = SCHEMA_FILE_MAP[test_type]['result_data']['schema_file']
        schema_verify_file = os.path.join(self.schema_base, schema_file_name)
        if not os.path.exists(schema_verify_file):
            return 'no file', "no schema file"
        result_file_name = SCHEMA_FILE_MAP[test_type]['result_data']['prod_file']
        test_result_file = os.path.join(self.test_output_base, executor, icu_version, result_file_name)
        results = {
            'test_type': test_type,
            'icu_version': icu_version,
            'executor': executor,
            'result': None,
            'err_info': None,
            'test_schema': schema_verify_file,
            'data_file_name': None
        }
        if not os.path.exists(test_result_file):
            results['data_file_name'] = None
            results['err_info'] = "no data file"
            return results
        results['data_file_name'] = test_result_file

        result = self.validate_json_file([schema_verify_file, test_result_file])
        results['result'] = result['result']
        results['err_info'] = result['error']
        if not results['result']:
            logging.error('Result data %s FAILED with %s ICU %s: %s', test_type, executor, icu_version, err_msg)

        return results

    def validate_schema_file(self, schema_file_path):
        test_type = os.path.basename(os.path.dirname(schema_file_path))
        try:
            schema_file = open(schema_file_path, encoding='utf-8', mode='r')
        except FileNotFoundError as err:
            return_error = err
            logging.error('  Cannot open data file %s.\n   Err = %s', schema_file_path, err)
            return False, err, schema_file_path, test_type

        # Get the schema file and validate the data against it
        try:
            schema = json.load(schema_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Error: %s Bad JSON schema: %s', err, schema_file_path)
            return False, err, schema_file_path, test_type

        try:
            validate(None, schema)
        except jsonschema.exceptions.SchemaError as err:
            return False, err
        except jsonschema.exceptions.ValidationError as err:
            # This is OK since it's only checking the schema's structure
            return True, '', schema_file_path, test_type

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

    def validate_test_output_parallel(self):
        test_validation_plans =  self.get_test_validation_plans();
        num_processors = mp.cpu_count()
        logging.info('JSON test output validation: %s processors for %s plans', num_processors, len(test_validation_plans))

        # How to get all the results
        processor_pool = mp.Pool(num_processors)
        with processor_pool as p:
            results = p.map(self.validate_json_file, test_validation_plans)

        return results, test_validation_plans

    def get_test_validation_plans(self):
        all_results = []
        test_validation_plans = []
        for executor in self.executors:
            for icu_version in self.icu_versions:
                for test_type in self.test_types:
                    schema_plan = self.get_test_output_schema_plan(icu_version, test_type, executor)
                    if schema_plan:
                        test_validation_plans.append(schema_plan)
        return test_validation_plans

    def validate_test_output_with_schema(self):
        return self.validate_test_output_parallel()

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
        logging.error('Not enough arguments provided')
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
            test_types = schema_files.ALL_TEST_TYPES
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

    schema_validator = ConformanceSchemaValidator()
    # Todo: use setters to initialize schema_validator
    schema_validator.schema_base = '.'
    schema_validator.test_data_base = os.path.split(base_folders[0])[0]
    schema_validator.test_output_base =  os.path.split(os.path.split(result_folders[0])[0])[0]
    schema_validator.icu_versions = ['icu71', 'icu72', 'icu73', 'icu74', 'icu75']
    schema_validator.executors = ['node', 'rust', 'dart_web', 'dart_native', 'icu4j']

    logging.info('Checking test outputs')
    all_test_out_results = schema_validator.validate_test_output_with_schema()
    for result in all_test_out_results:
        logging.debug('  %s', result)

    # Check all schema files for correctness.
    schema_errors = schema_validator.check_schema_files()
    if schema_errors:
        logging.error('INVALID SCHEMA: %s', schema_errors)
    else:
        logging.info('All schemas are valid: %s', schema_errors)

    icu_versions = ['icu71', 'icu72', 'icu73', 'icu74']
    executor_list = ['node', 'rust', 'dart_web', 'dart_native']

    logging.info('Checking generated data')
    all_test_data_results = schema_validator.validate_test_data_with_schema()
    for result in all_test_data_results:

        logging.debug('  %s', result)

    logging.info('Checking test outputs')
    all_test_out_results = schema_validator.validate_test_output_with_schema()
    for result in all_test_out_results:
        logging.debug('  %s', result)
    return

if __name__ == "__main__":
    main(sys.argv)

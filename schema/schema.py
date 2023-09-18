# Schema handling for test data, verification data, results files, etc.
# For ICU Conformance project, Data Driven Testing

import json
from jsonschema import validate
from jsonschema import ValidationError
from jsonschema import exceptions

import logging
import os.path
import sys

from schema_files import schema_file_map, all_test_types

# ?? Move to the initialization
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Given a directory, validate JSON files against expected schema
class ddt_validate():
    def __init__(self, folder_path=None):
        self.folder = ''
        self.valid_folder = False
        if folder_path:
            self.set_folder(folder_path)
        self.result_path = None

        self.schema_folder = '.'

    def set_folder(self, folder_path):
        # Folder typically contains an icu version, e.g., 'icu73'
        self.folder = folder_path

        self.valid_folder = os.path.isdir(folder_path)

    def set_result_path(self, path):
        self.result_path = path

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

    def validate_json_structure(self, test_type, data_paths, schema_paths, data_type):
        # Data type: one of 'test_data', verify_data', result_data" indicating which to verify
        # Get the data and the corresponding schema file.
        schema_file = open(schema_paths[data_type], encoding='utf-8', mode='r')
        data_file = open(data_paths[data_type], encoding='utf-8', mode='r')
        # Get the schema file and validate the data against it

        try:
            schema = json.load(schema_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON schema: %s', schema_paths[data_type])
            logging.error('  Error is %s', err)
            return False

        try:
            data_to_check = json.load(data_file)
        except json.decoder.JSONDecodeError as err:
            logging.error('Bad JSON data: %s', data_paths[data_type])
            logging.error('  Error is %s', err)
            return False

        # Now check this!
        try:
            validate(data_to_check, schema)
            logging.info('This one validates: %s, %s, %s:', test_type, data_paths[data_type], schema_paths[data_type] )
            return True
        except ValidationError as err:
            logging.error('Cannot validate %s with data %s and schema %s. ', test_type, data_paths[data_type], schema_paths[data_type] )
            logging.error('  Error = %s', err)
            return False
        except exceptions.SchemaError as err:
            logging.error('Cannot validate %s with data %s and schema %s. ', test_type, data_paths[data_type], schema_paths[data_type] )
            logging.error('  Error = %s', err)
            return False

        return

    def check_schema(self, test_type):

        return
def main(args):
    # Get name of test and type
    if len(args) < 2:
        print('you gotta give me something...')
        return

    base_folder = args[1]
    test_types = []
    if len(args) > 2:
        test_type = args[2]
        if test_type == "ALL":
            test_types = all_test_types
        else:
            test_types = [test_type]

    else:
        test_type = None

    if len(args) > 3:
        result_base = args[3]
    else:
        result_base = None

    validator = ddt_validate(base_folder)
    validator.set_result_path(result_base)

    for test_type in test_types:
        data_paths = validator.test_data_paths(test_type)
        schema_paths = validator.schema_paths((test_type))

        if not data_paths:
            print('No data_paths found for %s' % test_type)
            return

        logging.info(data_paths)
        logging.info(schema_paths)

    # TODO: Now, what should this do?
    #    validator.check_schema(test_type)

        json_date = data_paths
        data_type_list = ['test_data', 'verify_data']  #   Add this later 'result_data']

        for data_type in data_type_list:
            is_valid = validator.validate_json_structure(test_type, data_paths, schema_paths, data_type)

            if is_valid:
                logging.info('VALID: %s %s %s %s', test_type, data_paths, schema_paths, data_type)
            else:
                logging.error('!!! INVALID JSON: %s %s %s %s', test_type, data_paths, schema_paths, data_type)


if __name__ == "__main__":
    main(sys.argv)

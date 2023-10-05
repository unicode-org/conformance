# Points to file names for each supported JSON files.

all_test_types = ['collation_short',
                  'number_format',
                  'language_names',
                  'likely_subtags']

test_file_to_test_type_map = {
    'collation_test': 'collation_short',
    'lang_name_test_file': 'language_names',
    'likely_subtags_test': 'likely_subtags',
    'num_fmt_test_file': 'number_fmt'
}

schema_file_map = {
    "collation_short": {
        "test_data": {
            "schema_file": "collation_short/test_schema.json",
            "prod_file": "collation_test.json"
        },
        "verify_data": {
            # For, eventually, checking the files created by the verifieos.path.splitext(path)r.
            "schema_file": "collation_short/verify_schema.json",
            "prod_file": "pass.json"
        },
        "result_data": {
            # For checking test outputs.
            "schema_file": "collation_short/result_schema.json",
            "prod_file": "collation_test.json"
        }
    },

    "number_format": {
        "test_data": {
            "schema_file": "number_format/test_schema.json",
            'prod_file': 'num_fmt_test_file.json'
        },
        "verify_data": {
            "schema_file": "number_format/verify_schema.json",
            'prod_file': 'pass.json'
        },
        "result_data": {
            "schema_file": "number_format/result_schema.json",
            "prod_file": 'num_fmt_test_file.json'
        }
    },
    "number_fmt": {
        "test_data": {
            "schema_file": "number_format/test_schema.json",
            'prod_file': 'num_fmt_test_file.json'
        },
        "verify_data": {
            "schema_file": "number_format/verify_schema.json",
            'prod_file': 'pass.json'
        },
        "result_data": {
            "schema_file": "number_format/result_schema.json",
            "prod_file": 'num_fmt_test_file.json'
        }
    },

    "language_names": {
        "test_data": {
            "schema_file": "language_names/test_schema.json",
            'prod_file': 'lang_name_test_file.json'
        },
        "verify_data": {
            "schema_file": "language_names/verify_schema.json",
            'prod_file': 'pass.json'
        },
        "result_data": {
            "schema_file": "language_names/result_schema.json",
            "prod_file": "lang_name_test_file.json"
        }
    },

    "lang_names": {
        "test_data": {
            "schema_file": "language_names/test_schema.json",
            'prod_file': 'lang_name_test_file.json'
        },
        "verify_data": {
            "schema_file": "language_names/verify_schema.json",
            'prod_file': 'pass.json'
        },
        "result_data": {
            "schema_file": "language_names/result_schema.json",
            "prod_file": "lang_name_test_file.json"
        }
    },
    "likely_subtags": {
        "test_data": {
            "schema_file": "likely_subtags/test_schema.json",
            'prod_file': 'likely_subtags_test.json'
        },
        "verify_data": {
            "schema_file": "likely_subtags/verify_schema.json",
            'prod_file': 'likely_subtags_verify.json'
        },
        "result_data": {
            "schema_file": "likely_subtags/result_schema.json",
            "prod_file": "likely_subtags_test.json"
        }
    },

    # Additional tests
}

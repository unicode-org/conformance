# Points to file names for each supported JSON files.

all_test_types = ['collation_short', 'number_format', 'language_names', 'likely_subtags']

schema_file_map = {
    "collation_short": {
        "test_data": {
            "schema_file": "collation_short/test_schema.json",
            "prod_file": "collation_test.json"
        },
        "verify_data": {
            "schema_file": "collation_short/verify_schema.json",
            "prod_file": "collation_verify.json"
        },
        "result_data": {
            "schema_file": "collation_short/esult_schema..json",
            "prod_file": "pass.json"
        }
    },

    "number_format": {
        "test_data": {
            "schema_file": "number_format/test_schema.json",
            'prod_file': 'num_fmt_test_file.json'
        },
        "verify_data": {
            "schema_file": "number_format/verify_schema.json",
            'prod_file': 'num_fmt_verify_file.json'
        },
        "result_data": {
            "schema_file": "number_format/esult_schema..json",
            "prod_file": "pass.json"
        }
    },

    "language_names": {
        "test_data": {
            "schema_file": "language_names/test_schema.json",
            'prod_file': 'lang_name_test_file.json'
        },
        "verify_data": {
            "schema_file": "language_names/verify_schema.json",
            'prod_file': 'lang_name_verify_file.json'
        },
        "result_data": {
            "schema_file": "language_names/esult_schema..json",
            "prod_file": "pass.json"
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
            "schema_file": "likely_subtags/esult_schema..json",
            "prod_file": "pass.json"
        }
    },

    # Additional tests
}

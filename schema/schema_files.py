# Points to file names for each supported JSON files.

all_test_types = ['collation_short', 'number_format', 'language_names', 'likely_subtags']

schema_file_map = {
    "collation_short": {
        "test_data": {
            "schema_file": "collation_test_schema.json",
            "prod_file": "collation_test.json"
        },
        "verify_data": {
            "schema_file": "collation_short_verify_schema.json",
            "prod_file": "collation_verify.json"
        },
        "result_data": {
            "schema_file": "collation_short_result_schema.json",
            "prod_file": "pass.json"
        }
    },

    "number_format": {
        "test_data": {
            "schema_file": "number_format_test_schema.json",
            'prod_file': 'num_fmt_test_file.json'
        },
        "verify_data": {
            "schema_file": "number_format_verify_schema.json",
            'prod_file': 'num_fmt_verify_file.json'
        },
        "result_data": {
            "schema_file": "number_format_result_schema.json",
            "prod_file": "pass.json"
        }
    },

    "language_names": {
        "test_data": {
            "schema_file": "language_names_test_schema.json",
            'prod_file': 'lang_name_test_file.json'
        },
        "verify_data": {
            "schema_file": "language_names_verify_schema.json",
            'prod_file': 'lang_name_verify_file.json'
        },
        "result_data": {
            "schema_file": "language_names_result_schema.json",
            "prod_file": "pass.json"
        }
    },

    "likely_subtags": {
        "test_data": {
            "schema_file": "likely_subtags_test_schema.json",
            'prod_file': 'likely_subtags_test.json'
        },
        "verify_data": {
            "schema_file": "likely_subtags_verify_schema.json",
            'prod_file': 'likely_subtags_verify.json'
        },
        "result_data": {
            "schema_file": "likely_subtags_result_schema.json",
            "prod_file": "pass.json"
        }
    },

    # Additional tests
}

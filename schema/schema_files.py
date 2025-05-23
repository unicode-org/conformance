# Points to file names for each supported JSON files.

ALL_TEST_TYPES = ['collation',
                  'datetime_fmt',
                  'lang_names',
                  'likely_subtags',
                  'list_fmt',
                  'message_fmt2',
                  'number_format',
                  'plural_rules',
                  'rdt_fmt',
                  'segmenter'
                  ]

TEST_FILE_TO_TEST_TYPE_MAP = {
    'collation_test': 'collation',
    'datetime_fmt_test_file': 'datetime_fmt',
    'datetime_fmt_test': 'datetime_fmt',
    'lang_name_test_file': 'lang_names',
    'lang_names_test_file': 'lang_names',
    'likely_subtags_test': 'likely_subtags',
    'list_fmt_test_file': 'list_fmt',
    'list_fmt_test': 'list_fmt',
    'message_fmt2_test_file': 'message_fmt2',
    'message_fmt2_test': 'message_fmt2',
    'num_fmt_test_file': 'number_fmt',
    'plural_rules_test_file': 'plural_rules',
    'plural_rules_test': 'plural_rules',
    'rdt_fmt_test_file': 'rdt_fmt',
    'rdt_fmt_test': 'rdt_fmt',
    'segmenter_test': 'segmenter'
}

SCHEMA_FILE_MAP = {
    "collation": {
        "test_data": {
            "schema_file": "collation/test_schema.json",
            "prod_file": "collation_test.json"
        },
        "verify_data": {
            # For, eventually, checking the expected output created by the test generator.

            "schema_file": "collation/verify_schema.json",
            "prod_file": "collation_verify.json"
        },
        "result_data": {
            # For checking test outputs.
            "schema_file": "collation/result_schema.json",
            "prod_file": "collation_test.json"
        }
    },

    "datetime_fmt": {
        "test_data": {
            "schema_file": "datetime_fmt/test_schema.json",
            'prod_file': 'datetime_fmt_test.json'
        },
        "verify_data": {
            "schema_file": "datetime_fmt/verify_schema.json",
            'prod_file': 'datetime_fmt_verify.json'
        },
        "result_data": {
            "schema_file": "datetime_fmt/result_schema.json",
            "prod_file": 'datetime_fmt_test.json'
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
            'prod_file': 'num_fmt_verify_file.json'
        },
        "result_data": {
            "schema_file": "number_format/result_schema.json",
            "prod_file": 'num_fmt_test_file.json'
        }
    },

    "lang_names": {
        "test_data": {
            "schema_file": "lang_names/test_schema.json",
            'prod_file': 'lang_name_test_file.json'
        },
        "verify_data": {
            "schema_file": "lang_names/verify_schema.json",
            'prod_file': 'lang_name_verify_file.json'
        },
        "result_data": {
            "schema_file": "lang_names/result_schema.json",
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

    "list_fmt": {
        "test_data": {
            "schema_file": "list_fmt/test_schema.json",
            'prod_file': 'list_fmt_test.json'
        },
        "verify_data": {
            "schema_file": "list_fmt/verify_schema.json",
            'prod_file': 'list_fmt_verify.json'
        },
        "result_data": {
            "schema_file": "list_fmt/result_schema.json",
            "prod_file": "list_fmt_test.json"
        }
    },

    "plural_rules": {
        "test_data": {
            "schema_file": "plural_rules/test_schema.json",
            'prod_file': 'plural_rules_test.json'
        },
        "verify_data": {
            "schema_file": "plural_rules/verify_schema.json",
            'prod_file': 'plural_rules_verify.json'
        },
        "result_data": {
            "schema_file": "plural_rules/result_schema.json",
            "prod_file": "plural_rules_test.json"
        }
    },

    "message_fmt2": {
        "test_data": {
            "schema_file": "message_fmt2/test_schema.json",
            'prod_file': 'message_fmt2_test.json'
        },
        "verify_data": {
            "schema_file": "message_fmt2/verify_schema.json",
            'prod_file': 'message_fmt2_verify.json'
        },
        "result_data": {
            "schema_file": "message_fmt2/result_schema.json",
            'prod_file': 'message_fmt2_test.json'
        }
    },

    "rdt_fmt": {
        "test_data": {
            "schema_file": "rdt_fmt/test_schema.json",
            'prod_file': 'rdt_fmt_test.json'
        },
        "verify_data": {
            "schema_file": "rdt_fmt/verify_schema.json",
            'prod_file': 'rdt_fmt2_verify.json'
        },
        "result_data": {
            "schema_file": "rdt_fmt/result_schema.json",
            "prod_file": "rdt_fmt_test.json"
        }
    },

    "segmenter": {
        "test_data": {
            "schema_file": "segmenter/test_schema.json",
            'prod_file': 'segmenter_test.json'
        },
        "verify_data": {
            "schema_file": "segmenter/verify_schema.json",
            'prod_file': 'segmenter2_verify.json'
        },
        "result_data": {
            "schema_file": "segmenter/result_schema.json",
            "prod_file": "segmenter_test.json"
        }
    },
    # Additional tests

}

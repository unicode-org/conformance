# -*- coding: utf-8 -*-
from datetime import datetime, timezone

import os
import json
import re
import logging
import math
import subprocess
from generators.base import DataGenerator


class DateTimeFmtGenerator(DataGenerator):
    json_test = {"test_type": "datetime_fmt"}
    json_verify = {"test_type": "datetime_fmt"}

    def generate_datetime_data_from_cldr(self, dt_json_path, run_limit=-1):
        # Get CLDR-derived date time json file and parse it
        # Optionally sample from it if run_limit > 1
        with open(dt_json_path, 'r', encoding="UTF-8") as dt_json_file:
            try:
                json_data = json.load(dt_json_file)
            except json.JSONDecodeError as err:
                return None

            test_cases = []
            verify_cases = []

            test_obj = {
                'Test scenario': 'datetime_fmt',
                'test_type': 'datetime_fmt',
                'description': 'date/time formatCLDR  test data',
                'icuVersion': self.icu_version,
                'cldrVersion': '??'
            }

            test_cases = []
            verify_cases = []
            verify_obj = {
                'test_type': 'datetime_fmt',
                'description': 'date/time format CLDR test data',
                'icuVersion': self.icu_version,
                'cldrVersion': '??'
            }
            # Get each entry and assemble the test data and verify data.
            label_num = -1
            desired_width = math.ceil(math.log10(len(json_data)))  # Based the size of json_data

            input_index = -1
            input_increment = 1
            if self.run_limit > 0:
                input_increment = math.floor(len(json_data) / self.run_limit)

            for test_item in json_data:
                input_index += 1
                label_num += 1

                if input_index % input_increment != 0:
                    continue

                label_str = str(label_num).rjust(desired_width, "0")
                # Construct options
                options = {}
                # Generate input string with "Z" and compute tz_offset_secs
                raw_input = test_item['input']
                start_index = raw_input.find('[')
                end_index = raw_input.find(']')
                raw_time = datetime.fromisoformat(raw_input[0:start_index])

                if start_index >= 0 and end_index > start_index:
                    timeZone = raw_input[start_index+1:end_index]
                    options['timeZone'] = timeZone

                # Set the options
                if 'dateLength' in test_item:
                    options['dateStyle'] = test_item['dateLength']
                if 'timeLength' in test_item:
                    options['timeStyle'] = test_item['timeLength']
                # Specifies if the expected output includes "at"
                if 'dateTimeFormatType' in test_item:
                    options['dateTimeFormatType'] = test_item['dateTimeFormatType']

                if 'calendar' in test_item:
                    options['calendar'] = test_item['calendar']
                    if options['calendar'] == 'gregorian':
                        options['calendar'] = 'gregory'

                if 'yearStyle' in test_item:
                    options['yearStyle'] = test_item['yearStyle']
                if 'zoneStyle' in test_item:
                    options['zoneStyle'] = test_item['zoneStyle']

                # Generate UTC time equivalent and get the offset in seconds
                u_time = raw_time.astimezone(timezone.utc)
                input_string = u_time.isoformat().replace('+00:00', 'Z')
                tz_offset_secs = raw_time.utcoffset().total_seconds()

                if 'classicalSkeleton' in test_item:
                    options['skeleton'] = test_item['classicalSkeleton']
                if 'semanticSkeleton' in test_item:
                    options['semanticSkeleton'] = test_item['semanticSkeleton']
                if 'semanticSkeletonLength' in test_item:
                    options['semanticSkeletonLength'] = test_item['semanticSkeletonLength']

                if 'hourCycle' in test_item:
                    options['hourCycle'] = test_item['hourCycle'].lower()

                new_test = {
                    'label': label_str,
                    'locale': test_item['locale'],
                    'input_string': input_string,
                    'options': options,
                    'tz_offset_secs': tz_offset_secs,
                    'original_input': raw_input}

                new_verify = {'label': label_str,
                              'verify': test_item['expected']
                }
                test_cases.append(new_test)
                verify_cases.append(new_verify)



            # Save output as: datetime_fmt_test.json and datetime_fmt_verify.json
            test_obj['tests'] = test_cases
            verify_obj['verifications'] = verify_cases
            # Create the hex hash values
            self.generateTestHashValues(test_obj)

            base_path = ''
            dt_test_path = os.path.join(base_path, 'datetime_fmt_test.json')
            dt_verify_path = os.path.join(base_path, 'datetime_fmt_verify.json')

            try:
                self.saveJsonFile(dt_test_path, test_obj, indent=2)
                self.saveJsonFile(dt_verify_path, verify_obj, indent=2)
            except BaseException as err:
                logging.error('!!! %s: Failure to save file %s', err, )
                return None

    def process_test_data(self):
        # Check for datetime.json which has been generated from CLDR data.
        dt_json_path = os.path.join('.', self.icu_version, 'datetime.json')
        if os.path.exists(dt_json_path):
            result = self.generate_datetime_data_from_cldr(dt_json_path, self.run_limit)
            return result
        else:
            return False

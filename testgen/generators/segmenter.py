# -*- coding: utf-8 -*-
import os
import json
import re
import logging
import subprocess
from generators.base import DataGenerator

class SegmenterGenerator(DataGenerator):
    json_test = {"test_type": "segmenter"}
    json_verify = {"test_type": "segmenter"}

    def process_test_data(self):
        # Use Node JS to create the .json files
        icu_nvm_versions = {
            'icu77': '24.0.0',
            'icu76': '23.11.0',
            'icu75': '22.9.0',
            'icu74': '21.6.0',
            'icu73': '20.1.0',
            'icu72': '18.14.2',
            'icu71': '18.7.0',
        }

        # Just copy the files from generators folder
        exec_list = ['node generators/segmenter_gen.js']
        if self.run_limit > 0:
            exec_list.append('-run_limit')
            exec_list.append(str(self.run_limit))

        if self.icu_version not in icu_nvm_versions:
            logging.warning('Generating segmenter data not configured for icu version %s', self.icu_version)
            return False

        # Set up Node version and call the generator
        nvm_version = icu_nvm_versions[self.icu_version]
        generate_command = 'source ~/.nvm/nvm.sh; nvm install %s; nvm use %s --silent; %s' %\
                           (nvm_version, nvm_version, ' '.join(exec_list))

        logging.debug('Running this command: %s', generate_command)
        result = subprocess.run(generate_command, shell=True)

        # Move results to the right directory
        mv_command = 'mv segmenter*.json %s' % self.icu_version
        result = subprocess.run(mv_command, shell=True)

        return result

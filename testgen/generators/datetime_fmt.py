# -*- coding: utf-8 -*-
import os
import json
import logging
import re
import tokenize

from generators.base import DataGenerator

class DateTimeFmtGenerator(DataGenerator):
    def process_test_data(self):
        result = None

        filename = "format.txt"
        filepath = os.path.join(self.icu_version, filename)

        # Get this file and tokenize it.
        tokens = None
        with tokenize.open(filepath) as f:
            tokens = tokenize.generate_tokens(f.readline)

            done = False
            while not done:
                try:
                    item = next(tokens)
                except StopIteration:
                    done = true

                if item['string'] == 
                print(item)

            # Now we should have the tokens.
            for token in tokens:
                print(token)
            # Remove comments: DOUBLESLASH through NL (new line)

        return result

# Templates for creating comparison pages in verifier
import glob
import json
import logging
import logging.config
from string import Template
import sys

class compareTemplate():
    def __init__(self):
        logging.config.fileConfig("../logging.conf")

        # Read the template data
        compare_template = ''
        filename = 'compare_template.html'
        try:
            template_file = open(filename, mode='r')
            compare_template = template_file.read()
            template_file.close()
        except:
            logging.error('Cannot open compare_template %s', filename)

        self.html_template =  Template(compare_template)

        # Template for picking tests - will be replaced by html generated in detail_template.html
        self.checkbox_test_template = Template(
            '<div id="$id_div"><input type=checkbox class="test_id" id="$id" name="$name" value="$value" onclick="checkboxChanged(this);"</input><label for="$id">$test_name</div>'
        )

    def reportOutline(self):
        return self.html_template

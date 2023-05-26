# Templates for creating reports in verifier
import glob
import json
import logging
from string import Template
import sys

class reportTemplate():
    def __init__(self):
        # Read the template data
        detail_template = ''
        filename = 'detail_template.html'
        try:
            template_file = open(filename, mode='r')
            detail_template = template_file.read()
            template_file.close()
        except:
            logging.error('Cannot open detail template %s', filename)

        self.html_template =  Template(detail_template)

        summary_template = ''
        filename = 'summary_template.html'
        try:
            template_file = open(filename, mode='r')
            summary_template = template_file.read()
            template_file.close()
        except:
            logging.error('Cannot open summary template %s', filename)

        self.summary_html_template = Template(summary_template)

        self.error_table_template = Template(
"""    <table id='test_error_table' >
       <tr><th width="10%">Label</th><th width="20%">Error</th><th>Error detail</th><th>Test input</th></tr>
       <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
      $test_error_table
    </table>
""")

        self.unsupported_table_template = Template(
"""    <table id='test_unsupported_table'>
       <tr><th width="10%">Label</th><th width="20%">Unsupported message</th><th>Details</th><th>Input data</th></tr>
       <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
      $test_unsupported_table
    </table>
""")

        self.fail_line_template = Template(
        '<tr id="$label"><td>$label</td><td>$expected</td><td>$result</td><td>$input_data</td></tr>'
    )

        self.test_error_detail_template = Template(
        '<tr id="$label"><td>$label</td><td>$error</td><td>$error_detail</td><td>$input_data</td></tr>'
    )

        self.test_error_summary_template = Template(
        '<tr><td>$error</td><td>$count</td></tr>'
    )

        self.summary_table_template = Template(
"""    <table id='$type_summary_table'">
       <tr><th width="10%">$type</th><th width="20%">Count</th></tr>
       <!-- For each failing test, output row with columns
           item, count -->
       $table_content
       </table>
""")

        self.test_unsupported_template = Template(
        '<tr id="$label"><td>$label</td><td>$unsupported</$unsupported><td>$error_detail</td><td>$input_data</td></tr>'
    )

        self.checkbox_option_template = Template(
        '<input type=checkbox id="$id" name="$name" value="$value" onclick="checkboxChanged(this);"</input><label for="$id">$count $id</label><br>'
    )

    def reportOutline(self):
        return self.html_template

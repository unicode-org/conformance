# Templates for creating reports in verifier
import glob
import json
from string import Template
import sys

class reportTemplate():
    def __init__(self):
        self.report_outline = \
"""<html>
 <head>
    <meta charset="UTF-8">
    <title>$test_type with $exec</title>
    <style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    padding: 15px;
    text-align: center;
    }
    </style>
    <script>
    function toggleElement(id) {
      const element = document.getElementById(id);
      if (element.style.display === "none") {
        element.style.display = "block";
      } else {
        element.style.display = "none";
      }
    }
    // For viewing certain kinds of problems.
    const test_error_labels =
      $test_error_labels;
    const unsupported_labels =
      $unsupported_labels;

    const characterized_failure_labels =
      $characterized_failure_labels;;
    </script>
  </head>
  <body>
    <h1>Verification report: $test_type on $exec</h1>
    <h2>Test details</h2>
    <p>$platform_info</p>
    <p>$test_environment</p>
    <p>Result file created: $timestamp
    <h2>Test summary</h2>
    <p>Total: $total_tests.
    <p>Pass: $passing_tests, Fail: $failing_tests, Errors: $error_count, Unsupported: $unsupported_count</p>
    <h2 id='testErrors'">Test Errors ($error_count)</h2>
    <h3>Summary of test errors</h3>
    $error_summary
    <details>
    <summary>Open for all test errors</summary>
    <h3>All errors</h3>
   $error_section
    </details>

    <h2 id='testUnsupported'>Unsupported Tests  ($unsupported_count)</h2>
<h3>Summary of unsupported</h3>
    $unsupported_summary
<details>
<summary>Open for all unsupported tests</summary>
    <h3>All unsupported results</h3>
    $unsupported_section
</details>

<h2 id='testFailures'>Failing tests detail ($failing_tests)</h2>
    <details>
       <summary>Open for all failing tests.</summary>
<table id='failing_tests_table' >
    <tr><th style="width:10%">Label</th><th style="width:20%">Expected result</th><th style="width:20%">Actual result</th><th>Test input</th></tr>
      <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
$failure_table_lines
</table>
    </details>
    <h3>Failures characterized</h3>
    $failures_characterized
</body>
</html>
"""
        self.html_template = Template(self.report_outline)

        self.error_table_template = Template(
"""    <table id='test_error_table' >
       <tr><th width="10%">Label</th><th width="20%">Error</th><th>Error detail</th><th>Test input</th></tr>
       <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
      $test_error_table
    </table>
"""
        )


        self.unsupported_table_template = Template(
"""    <table id='test_unsupported_table'>
       <tr><th width="10%">Label</th><th width="20%">Unsupported message</th><th>Details</th><th>Input data</th></tr>
       <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
      $test_unsupported_table
    </table>
""")

        self.fail_line_template = Template(
        '<tr><td>$label</td><td>$expected</td><td>$result</td><td>$input_data</td></tr>'
    )

        self.test_error_detail_template = Template(
        '<tr><td>$label</td><td>$error</td><td>$error_detail</td><td>$input_data</td></tr>'
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
        '<tr><td>$label</td><td>$unsupported</$unsupported><td>$error_detail</td><td>$input_data</td></tr>'
    )

    def reportOutline(self):
        return self.html_template

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
    <!-- https://blueprintcss.dev/docs -->
    <link href="https://unpkg.com/blueprint-css@3.1.3/dist/blueprint.min.css" rel="stylesheet" />
    <title>$test_type with $exec</title>
    <style>
    body {   font-family: Sans-Serif; }

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

    const characterized_failure_labels =
      $characterized_failure_labels;

    let selectedSet = null;
    let accum_boxes = [];
    function checkboxChanged(box) {
      // Update the group selected with the intersection of values
      selectedSet = null;
      let first = true;
      for (let index in characterized_failure_labels) {
        const tag = characterized_failure_labels[index];
        const check_item = document.getElementById(tag);
        if (check_item.checked) {
          const label_string = check_item.value;
          const str_len = label_string.length;
          const labels = label_string.substring(2, str_len - 2). split("', '");
          const newSet = new Set(labels);

          if (first) {
             selectedSet = newSet;
             first = false;
          } else {
             selectedSet = new Set([...selectedSet].filter((x) => newSet.has(x)));
          }
        }
      }
     // Do something with the selected set.
     const newSize = selectedSet == null ? 0 : selectedSet.size;
     const output = document.getElementById('selectedCount');
     if (output) output.innerHTML = output.value = newSize;
     return newSize;
    }

    function showSelectedItems() {
      // Take the selected set and turn on row with that label in the tables.
      // Turn off the others.

      // If no items are selected, however, show all rows.
      let all_tr_elements = document.body.getElementsByTagName("tr");
      if (selectedSet == null || selectedSet.length == 0) {
        // Turn everything on!
        for (let index in all_tr_elements) {
          let element = all_tr_elements[index];
          if (element.style) {
            element.style.visibility = "visible";
            element.style.display = "table-row";
          }
        }
        return;
      }
      for (let index in all_tr_elements) {
        // Display only those selected.
        let element = all_tr_elements[index];
        const id = element.id;
        if (id) {
          if (selectedSet.has(id)) {
            // Show it
              if (element.style) {
                element.style.visibility = "visible";
                element.style.display = "table-row";
              }
            } else {
            // Turn it off
            if (element.style) {
              element.style.visibility = "collapse";
              //element.style.display = "none";
            }
          }
        }
      }
    }
    </script>
  </head>
  <body>
    <h1>Verification report: $test_type on $exec</h1>
    <h2>Test details</h2>
    <details>
      <summary>
    <p>$platform_info</p>
<p>Open for details</p>
</summary>
    <p>$test_environment</p>
</details>
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
   <div bp="grid">
     <div bp="16">
   $error_section
     </div>
     <div bp="6">
       Summary details
     </div>
   </div>
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
<div bp="grid">
  <div bp="20">
<table id='failing_tests_table' >
    <tr><th style="width:10%">Label</th><th style="width:20%">Expected result</th><th style="width:20%">Actual result</th><th>Test input</th></tr>
      <!-- For each failing test, output row with columns
           label, expected, actual, difference -->
$failure_table_lines
</table>
  </div>
  <div bp="4">
    <h3>Failures characterized</h3>
    <p>Filtered count = <span id='selectedCount'>0</span>
    <button id="showSelected" onclick="showSelectedItems();">"Update display"</button>
    </p>$failures_characterized
  </div>
</div>
    </details>
</body>
</html>
"""
        self.html_template = Template(self.report_outline)

        self.summary_html_template = Template(
"""<html>
  <head>
    <meta charset="UTF-8">
    <!-- https://blueprintcss.dev/docs -->
    <link href="https://unpkg.com/blueprint-css@3.1.3/dist/blueprint.min.css" rel="stylesheet" />
    <title>DDT Summary</title>
    <style>
    body {   font-family: Sans-Serif; }

    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    padding: 15px;o
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
    </script>
  </head>
  <body>
    <h1>Data Driven Test Summary</h1>
    <h3>Report generated: $datetime</h3>
    <h2>Tests and platforms</h2>
    <p>Executors verified: $all_platforms</p>
    <p>Tests verified: $all_tests</p>
    <h2>All Tests Summary</h2>
    <table id='exec_test_table'>
    $exec_header_line
    $detail_lines
    </table>
  </body>
</html>
""")

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

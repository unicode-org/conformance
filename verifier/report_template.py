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

    body {   font-family: Sans-Serif; }

    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    padding: 15px;o
    text-align: center;
    }
  </style>

    <!--Load the AJAX API for visualizing stacked bars-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

    <!-- JQuery -->
<script src="https://code.jquery.com/jquery-3.6.4.min.js" integrity="sha256-oP6HI9z1XaZNBrJURtCoUT5SUnxFr8s3BzRl+cbzUq8=" crossorigin="anonymous"></script>
    <script type="text/javascript">

      // Load the Visualization API and the corechart package.
      google.charts.load('current', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.charts.setOnLoadCallback(drawChart);

     // Callback that creates and populates a data table
     // Instantiates it with data, and draws it.
     // TODO: Update with all the data loaded
     function drawChart() {
       // For each test type:
       //   Get a div for the chart
       let chart = document.getElementById('chart_div')
       //   Create data for each executor in all versions under that test type
       //   Set up options and links
       //   Get the div where the output should be drawn s chart
       if (chart) {
         chart.draw(data, options);
       }
     }
</script>

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

    function loadJson(json_data) {

    }

    // Get up the JSON data from the tests.
    let pass_json;
    let fail_json;
    let error_json;
    let unsupported_json;

    fetch('./pass/pass.json')
      .then((response) => response.json())
      .then((data) => {pass_json = data});
    fetch('./failing_tests/failing_tests.json')
      .then((response) => response.json())
      .then((data) => {fail_json = data});
    fetch('./test_errors/test_errors.json')
      .then((response) => error_json = response.json())
      .then((data) => {error_json = data});
    fetch('./unsupported/unsupported.json')
      .then((response) => unsupportd_json = response.json())
      .then((data) => {unsupported_json = data});
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
    <h2 id='passingTests'>Passing tests</h2>
    <button onclick="loadJson('./pass/pass.json')">Load passing tests</button>

    <h2 id='testErrors'>Test Errors ($error_count)</h2>
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

<table id='passing_tests_table' >
    <tr><th style="width:10%">Label</th><th style="width:20%">Expected result</th><th style="width:20%">Actual result</th><th>Test input</th></tr>
      <!-- For each passing test, create the output line with label
           -->
</table>

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

    <!--Load the AJAX API for visualizing stacked bars-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <!-- JQuery -->
<script src="https://code.jquery.com/jquery-3.6.4.min.js" integrity="sha256-oP6HI9z1XaZNBrJURtCoUT5SUnxFr8s3BzRl+cbzUq8=" crossorigin="anonymous"></script>
    <script type="text/javascript">

    // The summary data for all the tests.
    let exec_summary_json;
    fetch('exec_summary.json')
      .then((response) => response.json())
      .then((data) => {exec_summary_json = data});

    function loadJson(json_data) {
      // For testing
    }

    // Load the Visualization API and the corechart package.
      google.charts.load('current', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.charts.setOnLoadCallback(drawChart);

     // Callback that creates and populates a data table
     // Instantiates it with data, and draws it.
     // TODO: Update with all the data loaded
     function drawChart() {
       // For each test type:
       let table = document.getElementById('exec_summary_table')

       let data_groups = ['Result', 'Pass', 'Fail', 'Error', 'Unsupported',
           {role: 'annotation'}];

       // Get all the types of tests available
       const test_types = Object.keys(exec_summary_json);
       /* Get all the execs */
       let tests_by_type_and_exec = {};

       // Find all the kinds of executors
       let execs = new Set();
       for (const test_type of test_types) {
         const tests = exec_summary_json[test_type];
         for (node_version of tests) {
           execs.add(node_version['exec']);
         }
       }

       // Create header ??
       let tr;
       let td;
       for (const test_type of test_types) {
         tr = table.insertRow();
         td = tr.insertCell();
         td.innerHTML = test_type

         const tests = exec_summary_json[test_type];
         for (const exec of execs) {
           td = tr.insertCell();

           // Get all the report info for this test and this exec
           let reports = [];
           let data = [data_groups];
           for (const report of tests) {
             if (report['exec'] == exec) {
               reports.push(report);
               // Add data for this report.
               const report_data = [
                 report['exec_version'],
                 report['pass_count'],
                 report['fail_count'],
                 report['error_count'],
                 report['unsupported_count'],
                 ''
               ];
               data.push(report_data);
             }
           }
           // Create the data for the reports
           // Make a new area for displaying ig.
           let options = {
             legend: {position: 'bottom', maxLines: 3},
             isStacked: true,
             width: 500, height:300, bar: {groupWidth: '75%' }
           };
           td = tr.insertCell();
           //   Set up options and links
           const chart = new google.visualization.BarChart(td);
           const chart_data = google.visualization.arrayToDataTable(data);
           if (reports && reports.length > 0 && chart) {  // TODO: debug
             chart.draw(chart_data, options);
          } else {
            td.innerHTML = "%s not tested in %s" % (test_type, exec);
            td.style.textAlign = "center";
          }
         }
       }
     }
  </script>

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

    <table id='exec_summary_table'>
    </table>

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

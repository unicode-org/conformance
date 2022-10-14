import json

class TestReport():
  # Holds information describing the results of running tests vs.
  # the expected results.
  def __init__(self):
    self.timestamp = None
    self.results = None
    self.verify = None

    self.title = ''

    self.report_file_path = None
    self.number_tests = None
    self.failing_tests = []
    self.tests_fail = 0
    self.passing_tests = []
    self.test_errors = []
    self.error_count = 0
    self.tests_pass = 0

    self.test_type = None
    self.executor = None

    self.platform = None

    self.missing_verify_data = []

  def recordFail(self, test):
    self.failing_tests.append(test)
    self.tests_fail += 1

  def recordPass(self, test):
    self.passing_tests.append(test)
    self.tests_pass += 1

  def recordTestError(self, test):
    self.test_errors.append(test)
    self.error_count +=1

  def recordMissingVerifyData(self, test):
    self.missing_verify_data.append(test)

  def summaryStatus(self):
    return self.tests_faile == 0 and self.missing_verify_data == []

  def createReport(self):
    # Make a JSON object with the data
    report = {}

    # Fill in the important fields.
    report['title'] = self.title

    report['timestamp'] = self.timestamp
    report['failCount'] = self.tests_fail
    report['passCount'] = self.tests_pass
    report['failingTests'] = self.failing_tests
    report['missing_verify_data'] = self.missing_verify_data
    report['test_error_count'] = self.error_count
    report['test_errors'] = self.test_errors
    self.report = report

    return json.dumps(report)

  def saveReport(self):
    try:
      file = open(self.report_file_path, mode='w', encoding='utf-8')
    except BaseException as err:
      std.err.write('!!! Cannot write report at %s: Error = %s' % (
          self.report_file_path, err))
      return None

    self.createReport()
    file.write(json.dumps(self.report))
    file.close()

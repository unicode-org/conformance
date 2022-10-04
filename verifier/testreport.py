import json

class TestReport():
  # Holds information describing the results of running tests vs.
  # the expected results.
  def __init__(self):
    self.timestamp = None
    self.results = None
    self.verify = None

    self.title = ''

    self.number_tests = None
    self.failing_tests = []
    self.tests_fail = 0
    self.passing_tests = []
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
    report['missing_verify_data'] = self.missing_verify_data

    return json.dumps(report)

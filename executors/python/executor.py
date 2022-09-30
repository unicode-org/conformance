# Test program to demonstrate command line --exec for
# general programs.

import json
import sys

class executor():
  def __init__(self):
    self.test_count = 0

  def handle_input(self, line):
    if line[0] == '#':
      platform_info = {
          'platform': 'python3 executor',
          'icuVersion': 'no version',
          }
      self.outline(platform_info)
    else:
      test_data = json.loads(line)
      test_data['test_IDq'] =  'TEST ' + test_data['label']
      test_data['python3_executor'] = True
      self.test_count += 1
      self.outline(test_data)
    return

  def outline(self, json_data):
    # Simply output to stdout
    sys.stdout.write(json.dumps(json_data))
    return


def main(args):
  inline = sys.stdin.readline()
  exec = executor()

  exec.handle_input(inline)

if __name__ == '__main__':
    main(sys.argv)

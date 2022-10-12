# Test program to demonstrate command line --exec for
# general programs.

import json
import sys

class executor():
  def __init__(self):
    self.test_count = 0
    self.debug = 1

  def handle_input(self):
    while True:
      inline = sys.stdin.readline()
      if self.debug:
        print('#INPUT = >%s<' % inline)
      if inline == "#EXIT":
        break
      elif inline == '#VERSION':
        platform_info = {
            'platform': 'python3 executor',
            'icuVersion': 'no version',
        }
        self.outline(platform_info)
      else:
        test_data = json.loads(inline)
        test_data['test_IDq'] =  'TEST ' + test_data['label']
        test_data['python3_executor'] = True
        self.test_count += 1
        self.outline(test_data)

    return

  def outline(self, json_data):
    # Simply output to stdout
    sys.stdout.write(json.dumps(json_data) + '\n')
    return


def main(args):
  exec = executor()

  exec.handle_input()

if __name__ == '__main__':
    main(sys.argv)

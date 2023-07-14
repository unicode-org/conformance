import 'dart:convert';
import 'dart:io';
import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

Map<String, List<String>> supportedTests = {
  'supported_tests': [
    'coll_shift_short',
    'decimal_fmt',
    'number_fmt',
    'display_names',
    'language_display_name',
  ],
};

enum TestTypes {
  coll_shift_short,
  decimal_fmt,
  datetime_fmt,
  display_names,
  lang_names,
  number_fmt;
}

void main() {
  stdin.listen((event) {
    var lines = utf8.decode(event);
    for (var line in lines.split('\n')) {
      if (line == '#EXIT') {
        exit(0);
      } else if (line == '#VERSION') {
        printVersion();
      } else if (line == '#TESTS') {
        print(json.encode(supportedTests));
      } else {
        Map<String, dynamic> decoded;
        try {
          decoded = json.decode(line);
        } catch (e) {
          print('ERROR $line');
          rethrow;
        }

        var testType = TestTypes.values
            .firstWhere((element) => element.name == decoded['test_type']);
        Object result;
        switch (testType) {
          case TestTypes.coll_shift_short:
            result = testCollator(decoded);
            break;
          case TestTypes.decimal_fmt:
          // TODO: Handle this case.
          case TestTypes.datetime_fmt:
          // TODO: Handle this case.
          case TestTypes.display_names:
          // TODO: Handle this case.
          case TestTypes.lang_names:
          // TODO: Handle this case.
          case TestTypes.number_fmt:
          // TODO: Handle this case.
          default:
            throw UnsupportedError('');
        }

        var outputLine = {'label': decoded['label'], 'result': result};
        print(json.encode(outputLine));
      }
    }
  });
}

bool testCollator(Map<String, dynamic> decoded) {
  var compared =
      Intl().collation(CollationOptions(ignorePunctuation: true)).compare(
            decoded['string1'],
            decoded['string2'],
          );
  var result = compared <= 0 ? true : false;
  return result;
}

void printVersion() {
  var version = Platform.version;
  var parsedVersion = version.substring(0, version.indexOf(' '));
  var versionInfo = {
    'icuVersion': '71.1',
    'platform': 'Dart',
    'platformVersion': parsedVersion,
  };
  print(json.encode(versionInfo));
}

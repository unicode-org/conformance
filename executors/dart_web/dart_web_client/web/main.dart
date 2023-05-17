import 'dart:collection';
import 'dart:convert';
import 'dart:html';
import 'package:intl4x/intl4x.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

enum TestTypes {
  coll_shift_short,
  decimal_fmt,
  datetime_fmt,
  display_names,
  lang_names,
  number_fmt;
}

var isDebug = false;

Queue<String> inputs = Queue();

Future<void> main() async {
  querySelector('#output')?.text = 'Loaded webpage.';

  final wsUrl = Uri.parse('ws://localhost:8081');
  var channel = WebSocketChannel.connect(wsUrl);

  channel.stream.listen((messageEndcoded) {
    inputs.add(messageEndcoded);
    if (isDebug) {
      channel.sink.add('#DEBUG: Received $messageEndcoded');
    }
  });

  while (true) {
    await Future.delayed(Duration(milliseconds: 50));
    popQueue(channel);
  }
}

void popQueue(WebSocketChannel channel) {
  if (inputs.isNotEmpty) {
    var messageEndcoded = inputs.removeFirst();
    if (messageEndcoded == '#EXIT') {
      channel.sink.add('#EXIT');
    } else {
      Map<String, dynamic> message = json.decode(messageEndcoded);
      var testType = TestTypes.values
          .firstWhere((element) => element.name == message['test_type']);
      Object result;
      switch (testType) {
        case TestTypes.coll_shift_short:
          result = testCollator(message);
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

      var outputLine = {'label': message['label'], 'result': result};
      channel.sink.add(json.encode(outputLine));
    }
  }
}

bool testCollator(Map<String, dynamic> decoded) {
  var compared = Intl().collation.compare(
        decoded['string1'],
        decoded['string2'],
      );
  return compared <= 0 ? true : false;
}

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:puppeteer/puppeteer.dart';
import 'package:shelf/shelf.dart';
import 'package:shelf/shelf_io.dart' as shelf_io;
import 'package:shelf_static/shelf_static.dart';
import 'package:shelf_web_socket/shelf_web_socket.dart';
import 'package:stream_channel/stream_channel.dart';

Map<String, List<String>> supportedTests = {
  'supported_tests': [
    'coll_shift_short',
    'decimal_fmt',
    'number_fmt',
    'display_names',
    'language_display_name',
  ],
};

bool isDebug = false;
Future<void> main(List<String> arguments) async {
  _debugWrite('Starting Executor');
  StreamChannel<dynamic>? webChannel;

  _debugWrite('Starting websocket server');
  var handler = webSocketHandler((StreamChannel<dynamic> webSocket) {
    _debugWrite('New connection $webSocket!');
    webChannel = webSocket;
  });
  await shelf_io.serve(handler, 'localhost', 8081);
  _debugWrite('Started websocket server');

  _debugWrite('Starting http server');
  final pipeline = const Pipeline()
      .addMiddleware(logRequests(
        logger: (message, isError) =>
            _debugWrite('Http Server ${isError ? 'ERR' : ''}: $message'),
      ))
      .addHandler(createStaticHandler(
          '../executors/dart_web/dart_web_client/build/',
          defaultDocument: 'index.html'));
  final server = await shelf_io.serve(pipeline, '127.0.0.1', 8084);
  _debugWrite('Started http server');

  var browser = await puppeteer.launch(headless: true);
  _debugWrite(browser.systemInfo.toString());

  var myPage = await browser.newPage();
  await Future.delayed(Duration(milliseconds: 2000));
  _debugWrite('Navigate to page');
  myPage.goto('http://127.0.0.1:8084');

  while (webChannel == null) {
    _debugWrite('Waiting for webchannel');
    await Future.delayed(Duration(milliseconds: 500));
  }
  _debugWrite('Started web client');

  webChannel!.stream.listen((message) async {
    var message2 = message as String;
    _debugWrite('WEB stream: $message2');
    if (message2.startsWith('#DEBUG')) {
      _debugWrite('WEB stream debug: $message');
    } else if (message == '#EXIT') {
      await terminate(server, browser);
    } else {
      print(message);
    }
  });

  stdin.listen((event) async {
    var lines = utf8.decode(event);
    for (var line in lines.split('\n')) {
      _debugWrite('In: $line');
      String output;
      if (line == '#EXIT') {
        _debugWrite('SEND: #EXIT');
        webChannel!.sink.add('#EXIT');
      } else if (line == '#VERSION') {
        output = printVersion();
        _debugWrite('Out: $output');
        print(output);
      } else if (line == '#TESTS') {
        output = json.encode(supportedTests);
        _debugWrite('Out: $output');
        print(output);
      } else {
        try {
          Map<String, dynamic> decoded = json.decode(line);
          var encoded = json.encode(decoded);
          _debugWrite('SEND: $encoded');
          webChannel!.sink.add(encoded);
        } catch (e) {
          _debugWrite('ERROR: $e at line $line');
        }
      }
    }
  });
}

Future<void> terminate(HttpServer server, Browser browser) async {
  server.close(force: true);
  await browser.close();
  await Future.delayed(Duration(milliseconds: 500));
  exit(0);
}

void _debugWrite(String contents) {
  if (isDebug) {
    var dateTime = DateTime.now();
    File('input.test.txt').writeAsStringSync(
      '${dateTime.hour}:${dateTime.minute}:${dateTime.second}:${dateTime.millisecond}\t$contents\n',
      mode: FileMode.append,
    );
  }
}

String printVersion() {
  var version = Platform.version;
  var parsedVersion = version.substring(0, version.indexOf(' '));
  var versionInfo = {
    'icuVersion': 'unknown',
    'platform': 'Dart',
    'platformVersion': parsedVersion,
  };
  return json.encode(versionInfo);
}

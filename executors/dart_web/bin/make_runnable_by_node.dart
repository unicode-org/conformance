import 'dart:io';

import 'package:pubspec_lock_parse/pubspec_lock_parse.dart';

Future<void> main(List<String> args) async {
  var name = 'collatorDart';
  var compile = await Process.run('dart', [
    'compile',
    'js',
    'bin/all_executors.dart',
    '-o',
    'out/$name.js',
  ]);
  print(compile.stderr);

  prepareOutFile(name, ['testCollationShort']);

  setVersionFile();
}

void setVersionFile() {
  var lockStr = File('pubspec.lock').readAsStringSync();

  final lockfile = PubspecLock.parse(lockStr);

  var version = lockfile.packages['intl4x']?.version;
  if (version != null) {
    File('out/version.js').writeAsStringSync('''
const dartVersion = "${version.canonicalizedVersion}";
module.exports = { dartVersion };
''');
  }
}

/// Prepare the file to export `testCollationShort`
void prepareOutFile(String name, List<String> functions) {
  var outFile = File('out/$name.js');
  var s = outFile.readAsStringSync();
  s = s.replaceAll('self.', '');
  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  var exportFunctions = functions
      .map(
        (e) => '''$e: function(arg) {
      return A.$e(arg);
    }''',
      )
      .join(',\n');
  s = s.replaceFirst(
    '})();\n\n//# sourceMappingURL=$name.js.map',
    '''
  return {
    $exportFunctions
  };
  })();
  //# sourceMappingURL=$name.js.map
  ''',
  );
  s = 'function dartMainRunner(main, args){}' + s;
  outFile.writeAsStringSync(s);
}

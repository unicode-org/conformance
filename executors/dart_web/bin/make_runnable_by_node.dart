import 'dart:io';

import 'package:pubspec_lock_parse/pubspec_lock_parse.dart';

class ExportFunction {
  final String name;
  final List<String> argNames;

  ExportFunction({required this.name, required this.argNames});
}

Future<void> main(List<String> args) async {
  var names = {
    'collator': ExportFunction(
      name: 'testCollationShort',
      argNames: ['encoded'],
    ),
    'numberformat': ExportFunction(
      name: 'testDecimalFormat',
      argNames: ['encoded', 'log', 'version'],
    ),
  };
  for (var name in names.entries) {
    await prepare(name.key, name.value);
  }

  setVersionFile();
}

Future<void> prepare(String name, ExportFunction function) async {
  var outFile = '${name}Dart';
  var compile = await Process.run('dart', [
    'compile',
    'js',
    'bin/${name}Executor.dart',
    '-O0',
    '-o',
    'out/$outFile.js',
  ]);
  print(compile.stderr);

  prepareOutFile(outFile, [function]);
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
void prepareOutFile(String name, List<ExportFunction> functions) {
  var outFile = File('out/$name.js');
  var s = outFile.readAsStringSync();
  s = s.replaceAll('self.', '');
  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  var exportFunctions = functions
      .map(
        (e) => '''${e.name}: function(${e.argNames.join(',')}) {
      return A.${e.name}(${e.argNames.join(',')});
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
  s = 'function dartMainRunner(main, args){}$s';
  outFile.writeAsStringSync(s);
}

import 'dart:io';

import 'package:pubspec_lock_parse/pubspec_lock_parse.dart';

class ExportFunction {
  final String name;
  final List<String> argNames;

  ExportFunction({required this.name, required this.argNames});
}

Future<void> main(List<String> args) async {
  final names = {
    'collator': ExportFunction(
      name: 'testCollationShort',
      argNames: ['encoded'],
    ),
    'numberformat': ExportFunction(
      name: 'testDecimalFormat',
      argNames: ['encoded', 'log', 'version'],
    ),
    'likely_subtags': ExportFunction(
      name: 'testLikelySubtags',
      argNames: ['encoded'],
    ),
    'lang_names': ExportFunction(
      name: 'testLangNames',
      argNames: ['encoded'],
    ),
  };
  for (final MapEntry(key: name, value: function) in names.entries) {
    await prepare(name, function);
  }

  setVersionFile();
}

Future<void> prepare(String name, ExportFunction function) async {
  final outFile = '${name}Dart';
  final compile = await Process.run('dart', [
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
  final lockStr = File('pubspec.lock').readAsStringSync();

  final lockfile = PubspecLock.parse(lockStr);

  final version = lockfile.packages['intl4x']?.version;
  if (version != null) {
    File('out/version.js').writeAsStringSync('''
const dartVersion = "${version.canonicalizedVersion}";
module.exports = { dartVersion };
''');
  }
}

/// Prepare the file to export `testCollationShort`
void prepareOutFile(String name, List<ExportFunction> functions) {
  final outFile = File('out/$name.js');
  var s = outFile.readAsStringSync();
  s = s.replaceAll('self.', '');
  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  final exportFunctions = functions
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

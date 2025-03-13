import 'dart:io';

import 'package:node_preamble/preamble.dart';
import 'package:pubspec_lock_parse/pubspec_lock_parse.dart';

class ExportFunction {
  final String name;
  final List<String> argNames;

  ExportFunction({required this.name, required this.argNames});
}

Future<void> main(List<String> args) async {
  final names = {
    'collator': ExportFunction(
      name: 'testCollation',
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
    await compile(name, function);
  }

  setVersionFile();
}

Future<void> compile(String name, ExportFunction function) async {
  final outfileName = 'out/${name}Dart.js';
  print('compile $name to $outfileName');
  final compile = await Process.run('dart', [
    'compile',
    'js',
    'bin/${name}Executor.dart',
    '-O0',
    '-o',
    outfileName,
  ]);
  print(compile.stdout);
  print(compile.stderr);
  final outFile = File(outfileName);
  exportFromJS('${name}Dart', outFile, function);
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

/// Prepare the file to export [name]
void exportFromJS(String name, File outFile, ExportFunction f) {
  var s = outFile.readAsStringSync();
  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  s = s.replaceFirst(
    '})();\n\n//# sourceMappingURL=$name.js.map',
    '''
  return {
    ${f.name}: function(${f.argNames.join(',')}) {
      return A.${f.name}(${f.argNames.join(',')});
    }
  };
  })();
  //# sourceMappingURL=$name.js.map
  ''',
  );
  s = 'function dartMainRunner(main, args){}$s';
  s = getPreamble() + s;
  outFile.writeAsStringSync(s);
}

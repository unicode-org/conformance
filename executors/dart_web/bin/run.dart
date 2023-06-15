import 'dart:io';

Future<void> main(List<String> args) async {
  var name = 'collatorDart';
  await Process.run('dart', [
    'compile',
    'js',
    'dart_web/bin/all_executors.dart',
    '-o',
    'dart_web/out/$name.js',
  ]);

  prepareOutFile(name);
}

/// Prepare the file to export `testCollationShort`
void prepareOutFile(String name) {
  var outFile = File('dart_web/out/$name.js');
  var s = outFile.readAsStringSync();
  s = s.replaceAll('self.', '');
  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  s = s.replaceFirst('(function dartProgram() {',
      'module.exports = (function dartProgram() {');

  s = s.replaceFirst(
    '''})();
  
  //# sourceMappingURL=$name.js.map''',
    '''
  return {
    testCollationShort: function(date) {
      return A.testCollationShort(date);
    }
  };
  })();
  //# sourceMappingURL=$name.js.map
  ''',
  );
  s = 'function dartMainRunner(main, args){}' + s;
  outFile.writeAsStringSync(s);
}

import 'dart:convert';
import 'dart:js_interop';

@JS('Intl.Locale')
extension type _LocaleJS._(JSObject _) implements JSObject {
  external factory _LocaleJS(String s);
  external _LocaleJS minimize();
  external _LocaleJS maximize();
  external String get baseName;
}

String testLikelySubtagsImpl(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;
  final label = json['label'];
  final localeStr = json['locale'] as String;
  final option = json['option'] as String;

  final returnJson = <String, dynamic>{'label': label};

  try {
    final locale = _LocaleJS(localeStr);
    if (option == 'maximize') {
      returnJson['result'] = locale.maximize().baseName;
    } else if (option == 'minimize' || option == 'minimizeFavorRegion') {
      returnJson['result'] = locale.minimize().baseName;
    } else {
      returnJson['error_type'] = 'unsupported';
      returnJson['unsupported'] = 'Option $option not supported on web';
      return jsonEncode(returnJson);
    }
  } catch (e) {
    returnJson['error'] = e.toString();
  }

  return jsonEncode(returnJson);
}

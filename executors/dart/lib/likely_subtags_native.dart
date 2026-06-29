import 'dart:convert';
import 'package:icu4x/icu4x.dart' as icu;

String testLikelySubtagsImpl(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;
  final label = json['label'];
  final localeStr = json['locale'] as String;
  final option = json['option'] as String;

  final returnJson = <String, dynamic>{'label': label};

  try {
    final locale = icu.Locale.fromString(localeStr);
    final expander = icu.LocaleExpander.extended();

    if (option == 'maximize') {
      expander.maximize(locale);
    } else if (option == 'minimize' || option == 'minimizeFavorRegion') {
      expander.minimize(locale);
    } else if (option == 'minimizeFavorScript') {
      expander.minimizeFavorScript(locale);
    } else {
      returnJson['error_type'] = 'unsupported';
      returnJson['unsupported'] = 'Unknown option: $option';
      return jsonEncode(returnJson);
    }

    returnJson['result'] = locale.toString();
  } catch (e) {
    returnJson['error'] = e.toString();
  }

  return jsonEncode(returnJson);
}

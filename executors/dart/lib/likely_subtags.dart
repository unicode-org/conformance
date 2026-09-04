import 'dart:convert';

import 'package:intl4x/locale.dart';

String testLikelySubtags(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;
  final label = json['label'];
  final localeStr = json['locale'] as String;
  final option = json['option'] as String;

  final returnJson = <String, dynamic>{'label': label};

  try {
    final locale = Locale.parse(localeStr);
    if (option == 'maximize') {
      returnJson['result'] = locale.maximize().toLanguageTag();
    } else if (option == 'minimize' || option == 'minimizeFavorRegion') {
      returnJson['result'] = locale.minimize().toLanguageTag();
    } else {
      returnJson['error_type'] = 'unsupported';
      returnJson['unsupported'] = 'Option $option not supported';
      return jsonEncode(returnJson);
    }
  } catch (e) {
    returnJson['error'] = e.toString();
  }

  return jsonEncode(returnJson);
}

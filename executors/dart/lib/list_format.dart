import 'dart:convert';
import 'package:collection/collection.dart';
import 'package:intl4x/list_format.dart'
    show ListStyle, Locale, ListType, ListFormat;

/// Tests Intl Locale for list formatting.
///
/// This function translates the logic from the given JavaScript code,
/// utilizing the `intl4x` package for `Intl.ListFormat` functionality.
String testListFmt(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;
  final label = json['label'];
  final returnJson = <String, dynamic>{'label': label};

  Locale? locale;
  final String? localeString = json['locale'];
  if (localeString != null) {
    try {
      locale = Locale.parse(localeString);
    } catch (e) {
      returnJson.addAll({
        'error': 'CONSTRUCTOR: Invalid locale format',
        'error_detail': e.toString(),
        'locale': localeString,
      });
      return jsonEncode(returnJson);
    }
  }

  final Map<String, dynamic>? optionsJson = json['options'];

  ListStyle? style;
  ListType? type;
  if (optionsJson != null) {
    try {
      style =
          ListStyle.values.firstWhereOrNull(
            (style) => style.name == optionsJson['style'] as String?,
          ) ??
          ListStyle.long;
      type = switch (optionsJson['list_type'] as String?) {
        'conjunction' => ListType.and,
        'disjunction' => ListType.or,
        'unit' => ListType.unit,
        _ => ListType.and,
      };
    } catch (e) {
      returnJson.addAll({
        'error': 'CONSTRUCTOR: Invalid options format',
        'error_detail': e.toString(),
        'options': optionsJson,
      });
      return jsonEncode(returnJson);
    }
  }

  final inputListDynamic = json['input_list'] as List?;
  if (inputListDynamic == null) {
    returnJson['error'] = 'Incomplete test: no input_list provided';
    return jsonEncode(returnJson);
  }
  final inputList = inputListDynamic.map((e) => e.toString()).toList();

  final listFormatter = switch ((style, type)) {
    (final s?, final t?) => ListFormat(locale: locale, style: s, type: t),
    (_, final t?) => ListFormat(locale: locale, type: t),
    (final s?, _) => ListFormat(locale: locale, style: s),
    (_, _) => ListFormat(locale: locale),
  };

  try {
    final result = listFormatter.format(inputList);
    returnJson['result'] = result;
  } catch (error) {
    returnJson['error'] = 'LIST FORMATTER UNKNOWN ERROR: ${error.toString()}';
  }

  return jsonEncode(returnJson);
}

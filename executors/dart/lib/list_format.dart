import 'dart:convert';
import 'package:intl4x/intl4x.dart';
import 'package:intl4x/list_format.dart'; // Import for ListFormat and ListFormatOptions

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

  ListFormatOptions? listFormatOptions;
  if (optionsJson != null) {
    try {
      //TODO parse options
      listFormatOptions = ListFormatOptions();
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

  final listFormatter = Intl(
    locale: locale,
  ).listFormat(listFormatOptions ?? ListFormatOptions());

  try {
    final result = listFormatter.format(inputList);
    returnJson['result'] = result;
  } catch (error) {
    returnJson['error'] = 'LIST FORMATTER UNKNOWN ERROR: ${error.toString()}';
  }

  return jsonEncode(returnJson);
}

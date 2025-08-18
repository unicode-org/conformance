import 'dart:convert';
import 'package:collection/collection.dart';
import 'package:intl4x/datetime_format.dart';
import 'package:intl4x/intl4x.dart';

/// Tests date/time formatting using intl4x.
///
/// This function translates the logic from the given JavaScript code,
/// utilizing the `intl4x` package for `Intl.DateTimeFormat` functionality.
String testDateTimeFmt(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  final label = json['label'];
  var localeString = json['locale'] as String?; // locale can be null from JSON
  if (localeString == null || localeString.isEmpty) {
    localeString = 'und'; // Default to 'und' if locale is null or empty
  }

  // Parse Locale string
  Locale locale;
  try {
    locale = Locale.parse(localeString.replaceAll('_', '-'));
  } catch (e) {
    return jsonEncode({
      'label': label,
      'error': 'Invalid locale format: ${e.toString()}',
      'locale': localeString,
    });
  }

  var testOptionsJson = <String, dynamic>{};
  if (json['options'] != null) {
    testOptionsJson = json['options'] as Map<String, dynamic>;
  }

  // Initialize DateTimeFormatOptions
  var dateTimeFormatOptions = DateTimeFormatOptions();

  // Handle calendar and timezone from test_optionsJson
  String? calendarString;
  if (testOptionsJson.containsKey('calendar')) {
    calendarString = testOptionsJson['calendar'] as String;
    // Note: intl4x's DateTimeFormatOptions directly supports calendar as a string.
    // However, checking supported calendars via `intl_locale.calendars`
    // is not directly available in `intl4x`'s current Locale API for all calendars.
    // If a calendar is unsupported, the `DateTimeFormat` constructor might throw,
    // or it might fall back. We'll rely on intl4x's internal handling.
    dateTimeFormatOptions = dateTimeFormatOptions.copyWith(
      calendar: Calendar.values.firstWhereOrNull(
        (calendar) => calendar.jsName == calendarString,
      ),
    );
  }

  // ignore: unused_local_variable - to be used with the timezoneformatter
  String? timezone;
  int? offset;
  String? timeZoneStyle;
  if (testOptionsJson.containsKey('time_zone') &&
      testOptionsJson.containsKey('tz_offset_secs') &&
      testOptionsJson.containsKey('timeStyle')) {
    timezone = testOptionsJson['time_zone'] as String;
    offset = testOptionsJson['tz_offset_secs'] as int;
    timeZoneStyle = testOptionsJson['timeStyle'] as String;
  }

  final dateStyle = testOptionsJson['dateStyle'] as String?;
  final timeStyle = testOptionsJson['timeStyle'] as String?;
  final yearStyle = testOptionsJson['yearStyle'] as String?;

  DateTime? testDate;
  if (json['input_string'] != null) {
    final isoDateString = json['input_string'] as String;
    // Remove anything starting with "[" (JS part to extract options from string)
    final optionStart = isoDateString.indexOf('[');
    String testDateString;
    if (optionStart >= 0) {
      testDateString = isoDateString.substring(0, optionStart);
    } else {
      testDateString = isoDateString;
    }
    try {
      testDate = DateTime.parse(testDateString);
    } catch (e) {
      return jsonEncode({
        'label': label,
        'error': 'Invalid input_string date format: ${e.toString()}',
        'input_string': isoDateString,
      });
    }
  } else {
    testDate = DateTime.now();
  }

  final returnJson = <String, dynamic>{'label': label};
  final dtFormatter = Intl(
    locale: locale,
  ).dateTimeFormat(dateTimeFormatOptions);

  try {
    final formatter = switch ((dateStyle, timeStyle, yearStyle)) {
      ('medium', null, _) => dtFormatter.ymd(dateStyle: DateFormatStyle.medium),
      (null, 'short', _) => dtFormatter.t(style: TimeFormatStyle.short),
      ('full', 'short', null) => dtFormatter.ymdt(
        dateStyle: DateFormatStyle.full,
        timeStyle: TimeFormatStyle.short,
      ),
      ('short', 'full', null) => dtFormatter.ymdt(
        dateStyle: DateFormatStyle.short,
        timeStyle: TimeFormatStyle.full,
      ),
      (_, _, 'with_era') => dtFormatter.ymde(),
      ('short', 'full', _) => dtFormatter.ymdet(
        dateStyle: DateFormatStyle.short,
        timeStyle: TimeFormatStyle.full,
      ),
      (_, _, _) => throw UnimplementedError(
        'Unknown combination of date style `$dateStyle`, time style `$timeStyle`, and year style `$yearStyle`',
      ),
    };
    String formattedDt;
    if (timezone != null) {
      final timeZone = TimeZone(
        name: timezone,
        offset: Duration(seconds: offset!),
      );
      final zonedFormatter = switch (timeZoneStyle!) {
        'short' => formatter.withTimeZoneShort(timeZone),
        'long' => formatter.withTimeZoneLong(timeZone),
        'full' => formatter.withTimeZoneLongGeneric(timeZone),
        String() => throw UnimplementedError(
          'Unknown time zone style `$timeZoneStyle`',
        ),
      };
      formattedDt = zonedFormatter.format(testDate);
    } else {
      formattedDt = formatter.format(testDate);
    }
    returnJson['result'] = formattedDt;
    returnJson['actual_options'] = dateTimeFormatOptions.humanReadable;
    returnJson['options'] = testOptionsJson;
  } catch (error) {
    returnJson['error'] = ': ${error.toString()}';
  }

  return jsonEncode(returnJson);
}

extension on DateTimeFormatOptions {
  String get humanReadable {
    final fields = <String, dynamic>{
      if (calendar != null) 'calendar': calendar,
      if (dayPeriod != null) 'dayPeriod': dayPeriod,
      if (numberingSystem != null) 'numberingSystem': numberingSystem,
      if (clockstyle != null) 'clockstyle': clockstyle,
      if (era != null) 'era': era,
      if (timestyle != null) 'timestyle': timestyle,
      if (fractionalSecondDigits != null)
        'fractionalSecondDigits': fractionalSecondDigits,
      'formatMatcher': formatMatcher,
    };
    final entries = fields.entries
        .map((e) => '${e.key}: ${e.value}')
        .join(', ');
    return 'DateTimeFormatOptions($entries)';
  }
}

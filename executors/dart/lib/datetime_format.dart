import 'dart:convert';

import 'package:collection/collection.dart';
import 'package:intl4x/datetime_format.dart';

/// Tests date/time formatting using intl4x.
///
/// This function translates the logic from the given JavaScript code,
/// utilizing the `intl4x` package for `Intl.DateTimeFormat` functionality.
String testDateTimeFmt(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  var localeString = json['locale'] as String?; // locale can be null from JSON
  if (localeString == null || localeString.isEmpty) {
    localeString = 'und'; // Default to 'und' if locale is null or empty
  }

  final returnJson = <String, dynamic>{'label': json['label']};

  // Parse Locale string
  Locale locale;
  try {
    locale = Locale.parse(localeString.replaceAll('_', '-'));
  } catch (e) {
    returnJson['error'] = 'Invalid locale format: ${e.toString()}';
    returnJson['locale'] = localeString;
    return jsonEncode(returnJson);
  }

  var testOptionsJson = <String, dynamic>{};
  if (json['options'] != null) {
    testOptionsJson = json['options'] as Map<String, dynamic>;
  }

  if (testOptionsJson['dateTimeFormatType'] == 'atTime') {
    returnJson['error_type'] = 'unsupported';
    returnJson['unsupported'] = '`at` not supported';
    return jsonEncode(returnJson);
  }

  // Initialize DateTimeFormatOptions
  // Handle calendar and timezone from test_optionsJson
  String? calendarString;
  Calendar? calendar;
  if (testOptionsJson.containsKey('calendar')) {
    calendarString = testOptionsJson['calendar'] as String;
    // Note: intl4x's DateTimeFormatOptions directly supports calendar as a string.
    // However, checking supported calendars via `intl_locale.calendars`
    // is not directly available in `intl4x`'s current Locale API for all calendars.
    // If a calendar is unsupported, the `DateTimeFormat` constructor might throw,
    // or it might fall back. We'll rely on intl4x's internal handling.
    calendar = Calendar.values.firstWhereOrNull(
      (calendar) => calendar.jsName == calendarString,
    );
  }

  // ignore: unused_local_variable - to be used with the timezoneformatter
  String? timeZoneName;
  int? offsetSeconds;
  if (testOptionsJson.containsKey('timeZone') &&
      json.containsKey('tz_offset_secs')) {
    timeZoneName = testOptionsJson['timeZone'] as String;
    offsetSeconds = (json['tz_offset_secs'] as num).toInt();
  }

  final skeleton = testOptionsJson['skeleton'] as String?;
  final semanticSkeleton = testOptionsJson['semanticSkeleton'] as String?;
  final semanticSkeletonLength =
      testOptionsJson['semanticSkeletonLength'] as String?;

  final dateStyle = testOptionsJson['dateStyle'] as String?;
  final timeStyle = testOptionsJson['timeStyle'] as String?;

  final timePrecision = switch (timeStyle) {
    'full' => TimePrecision.second,
    'long' => TimePrecision.second,
    'medium' => TimePrecision.second,
    'short' => TimePrecision.minute,
    _ => null,
  };
  final yearStyle = switch (testOptionsJson['yearStyle'] as String?) {
    'with_era' => YearStyle.withEra,
    _ => null,
  };

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
      returnJson['error'] = 'Invalid input_string date format: ${e.toString()}';
      returnJson['input_string'] = isoDateString;
      return jsonEncode(returnJson);
    }
  }

  try {
    final formatter = semanticSkeleton != null
        ? getFormatterForSkeleton(
            semanticSkeleton,
            semanticSkeletonLength,
            locale,
            yearStyle,
            timePrecision,
          )
        : getFormatterForStyle(
            dateStyle,
            timeStyle,
            yearStyle,
            locale,
            timePrecision,
          );
    String formattedDt;
    if (formatter is DateTimeFormatter &&
        (semanticSkeleton ?? '').contains('Z')) {
      final offset = Duration(seconds: offsetSeconds!);
      final zoneStyle = testOptionsJson['zoneStyle'] as String?;
      final zonedFormatter = getZonedFormatter(zoneStyle, formatter, skeleton);
      formattedDt = zonedFormatter.format(testDate!.add(offset), timeZoneName!);
    } else {
      formattedDt = formatter.format(testDate!);
    }
    returnJson['result'] = formattedDt;
  } on Exception catch (e) {
    returnJson['error_type'] = 'unsupported';
    returnJson['unsupported'] = ': ${e.toString()}';
    return jsonEncode(returnJson);
  }
  returnJson['actual_options'] = {
    'locale': locale.toString(),
    if (dateStyle != null) 'dateStyle': dateStyle,
    if (timeStyle != null) 'timeStyle': timeStyle,
    if (yearStyle != null) 'yearStyle': yearStyle.name,
    if (calendar != null) 'calendar': calendar.jsName,
  };
  returnJson['options'] = testOptionsJson;

  return jsonEncode(returnJson);
}

DateTimeFormatterStandalone getFormatterForSkeleton(
  String semanticSkeleton,
  String? semanticSkeletonLength,
  Locale locale,
  YearStyle? yearStyle,
  TimePrecision? timePrecision,
) {
  // The provided Rust code implies a more complex logic, but here we'll map the known skeletons.
  // The Rust code's `None => None` and `None => Ok(...)` branches aren't directly translatable
  // to a Dart function that must return a Formatter. We'll handle the valid cases and throw for others.

  final semanticDateStyle = switch (semanticSkeletonLength) {
    'short' => DateTimeLength.short,
    'medium' => DateTimeLength.medium,
    'long' => DateTimeLength.long,
    _ => throw Exception(),
  };

  return switch (semanticSkeleton) {
    'D' ||
    'DT' ||
    'DTZ' => DateTimeFormat.day(locale: locale, length: semanticDateStyle),
    'MD' => DateTimeFormat.monthDay(locale: locale, length: semanticDateStyle),
    'MDT' || 'MDTZ' => DateTimeFormat.monthDayTime(
      locale: locale,
      length: semanticDateStyle,
      timePrecision: timePrecision,
    ),
    'YMD' || 'YMDT' || 'YMDTZ' => DateTimeFormat.yearMonthDay(
      locale: locale,
      length: semanticDateStyle,
    ),
    'YMDE' => DateTimeFormat.yearMonthDayWeekday(
      locale: locale,
      length: semanticDateStyle,
      yearStyle: yearStyle,
    ),
    'YMDET' || 'YMDETZ' => DateTimeFormat.yearMonthDayWeekdayTime(
      locale: locale,
      length: semanticDateStyle,
      timePrecision: timePrecision,
    ),
    'M' => DateTimeFormat.month(locale: locale, length: semanticDateStyle),
    'Y' => DateTimeFormat.year(locale: locale, length: semanticDateStyle),
    'T' || 'TZ' => DateTimeFormat.time(
      locale: locale,
      length: semanticDateStyle,
      timePrecision: timePrecision,
    ),
    _ => throw Exception('Unknown skeleton: $semanticSkeleton'),
  };
}

ZonedDateTimeFormatter getZonedFormatter(
  String? timeZoneStyle,
  DateTimeFormatter formatter,
  String? skeleton,
) {
  if (skeleton != null) {
    // Long Generic
    if (skeleton.contains('vvvv') || skeleton.contains('VVVV')) {
      return formatter.withTimeZoneLongGeneric();
    }
    // Short Generic
    else if (skeleton.contains('v') || skeleton.contains('V')) {
      return formatter.withTimeZoneShortGeneric();
    }
    // Long Offset
    else if (skeleton.contains('OOOO')) {
      return formatter.withTimeZoneLongOffset();
    }
    // Short Offset
    else if (skeleton.contains('O')) {
      return formatter.withTimeZoneShortOffset();
    }
    // Long Specific (Name)
    else if (skeleton.contains('zzzz')) {
      return formatter.withTimeZoneLong();
    }
    // Short Specific (Name)
    else if (skeleton.contains('z')) {
      return formatter.withTimeZoneShort();
    }
  }
  return switch (timeZoneStyle) {
    'short' => formatter.withTimeZoneShort(),
    'specific' => formatter.withTimeZoneShort(),
    'full' => formatter.withTimeZoneLongGeneric(),
    'generic' => formatter.withTimeZoneLongGeneric(),
    'location' => formatter.withTimeZoneShort(),
    'offset' => formatter.withTimeZoneLongGeneric(),
    null => formatter.withTimeZoneLongGeneric(),
    String() => throw Exception('Unknown time zone style `$timeZoneStyle`'),
  };
}

DateTimeFormatter getFormatterForStyle(
  String? dateStyle,
  String? timeStyle,
  YearStyle? yearStyle,
  Locale locale,
  TimePrecision? timePrecision,
) {
  print((dateStyle, timeStyle, yearStyle));
  return switch ((dateStyle, timeStyle, yearStyle)) {
    ('medium', null, null) => DateTimeFormat.yearMonthDay(
      locale: locale,
      length: DateTimeLength.medium,
    ),
    (null, 'short', _) => DateTimeFormat.time(
      locale: locale,
      length: DateTimeLength.short,
      timePrecision: timePrecision,
    ),
    ('full', 'short', null) => DateTimeFormat.yearMonthDayWeekdayTime(
      locale: locale,
      length: DateTimeLength.long,
      timePrecision: timePrecision,
    ),
    ('full', 'full', null) => DateTimeFormat.yearMonthDayWeekdayTime(
      locale: locale,
      length: DateTimeLength.long,
      timePrecision: timePrecision,
    ),
    ('short', 'full', null) => DateTimeFormat.yearMonthDayTime(
      locale: locale,
      length: DateTimeLength.short,
    ),
    ('short', 'full', YearStyle.withEra) =>
      DateTimeFormat.yearMonthDayWeekdayTime(
        locale: locale,
        length: DateTimeLength.short,
        yearStyle: yearStyle,
        timePrecision: timePrecision,
      ),
    (_, _, YearStyle.withEra) => DateTimeFormat.yearMonthDayWeekday(
      locale: locale,
      yearStyle: yearStyle,
    ),
    (_, _, _) => throw Exception(
      'Unknown combination of date style `$dateStyle`, time style `$timeStyle`, and year style `$yearStyle`',
    ),
  };
}

// Copied from intl4x/lib/src/locale/locale.dart
extension CalendarJsName on Calendar {
  /// Returns the JavaScript-compatible name for the calendar.
  ///
  /// This implementation uses a switch expression to map specific enum
  /// values to their corresponding JS names, falling back to the enum's
  /// `name` for others.
  String get jsName => switch (this) {
    Calendar.traditionalChinese => 'chinese',
    Calendar.traditionalKorean => 'dangi',
    Calendar.ethiopianAmeteAlem => 'ethioaa',
    Calendar.ethiopian => 'ethiopic',
    Calendar.gregorian => 'gregory',
    Calendar.hijriUmalqura => 'islamic-umalqura',
    Calendar.hijriTbla => 'islamic-tbla',
    Calendar.hijriCivil => 'islamic-civil',
    Calendar.minguo => 'roc',
    _ => name,
  };
}

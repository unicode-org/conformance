import 'dart:convert';

import 'package:collection/collection.dart';
import 'package:intl4x/datetime_format.dart';
import 'package:intl4x/number_format.dart';
// ignore: implementation_imports
import 'package:intl4x/src/ecma/ecma_native.dart'
    if (dart.library.js_interop) 'package:intl4x/src/ecma/ecma_web.dart';
// ignore: implementation_imports
import 'package:intl4x/src/number_format/number_format_impl.dart';
// ignore: implementation_imports
import 'package:intl4x/src/number_format/number_format_options.dart';

String testDecimalFormat(String encoded, bool loggingEnabled, String version) {
  return testDecimalFormatWrapped(encoded, loggingEnabled);
}

final _patternsToOptions = <String, NumberFormatOptions>{
  '0.0': NumberFormatOptions.custom(
    digits: Digits.withFractionDigits(minimum: 1),
  ),
  '00': NumberFormatOptions.custom(
    digits: Digits.withSignificantDigits(minimum: 1),
  ),
  '@@@': NumberFormatOptions.custom(
    digits: Digits.withSignificantDigits(minimum: 3),
  ),
  '@@###': NumberFormatOptions.custom(
    digits: Digits.withSignificantDigits(minimum: 2, maximum: 5),
  ),
  '0.0000E0': NumberFormatOptions.custom(
    notation: ScientificNotation(),
    digits: Digits.withFractionDigits(minimum: 4),
  ),
};

const _unsupportedSkeletonTerms = [
  'scientific/+ee/sign-always',
  'decimal-always',
];

String testDecimalFormatWrapped(String encoded, [bool loggingEnabled = false]) {
  final json = jsonDecode(encoded) as Map<String, dynamic>;
  final label = json['label'] as String?;
  final skeleton = json['skeleton'] as String?;
  final pattern = json['pattern'] as String?;
  final rounding = json['rounding'] as String?;
  var input = double.parse(
    json['input'] as String,
  ); // May be changed with some options

  // If options are in the JSON, use them...
  NumberFormatOptions options;
  final jsonOptions = (json['options'] ?? {}) as Map<String, dynamic>;
  if (jsonOptions.isNotEmpty) {
    try {
      options = _fromJson(jsonOptions);
    } catch (e) {
      // This is a special kind of unsupported.
      return jsonEncode({
        'label': label,
        'unsupported': 'parsing error',
        'error_type': 'unsupported',
        'error': 'Option parsing error: $e',
      });
    }
  } else {
    try {
      options = _decimalPatternToOptions(pattern, rounding);
    } catch (error) {
      // Some error - to return this message
      return jsonEncode({
        'error': error.toString(),
        'error_type': 'unsupported',
        'label': label,
      });
    }
  }

  if (!useBrowser &&
      (options.style is UnitStyle ||
          options.style is PercentStyle ||
          options.style is CurrencyStyle)) {
    return jsonEncode({
      'error': 'Unit, percent, or currency style are not supported yet',
      'error_type': 'unsupported',
      'unsupported': 'unsupported_options',
      'label': label,
    });
  }
  // Default maximumFractionDigits and rounding modes are set in test generation

  // Check each option for implementation.
  // Handle percent - input value is the basis of the actual percent
  // expected, e.g., input='0.25' should be interpreted '0.25%'
  if (options.style is PercentStyle) {
    input = input / 100.0;
  }

  // Handle scale in the skeleton
  final skeletonTerms = skeleton?.split(' ') ?? [];
  if (skeleton != null) {
    if (loggingEnabled) {
      print('# SKEL: $skeletonTerms');
    }
    final scaleRegex = RegExp(r'scale/(\d+\.\d*)');
    final matchScale = scaleRegex.firstMatch(skeleton);
    if (matchScale != null) {
      // Get the value and use it
      final scaleValue = double.parse(matchScale.group(1)!);
      input = input * scaleValue;
    }
  }

  final unsupportedOptions = _getUnsupportedSkeletonterms(
    skeletonTerms,
    loggingEnabled,
  );

  if (unsupportedOptions.isNotEmpty) {
    return jsonEncode({
      'label': label,
      'unsupported': 'unsupported_options',
      'error_type': 'unsupported',
      'error_detail': {'unsupported_options': unsupportedOptions},
    });
  }

  final testLocale = json['locale'] as String?;

  Map<String, dynamic> outputLine;
  Locale locale;
  try {
    if (testLocale != null) {
      locale = Locale.parse(testLocale);
    } else {
      locale = Locale.parse('und');
    }
    final nf = NumberFormatImpl.build(locale, options);

    // TODO: Catch unsupported units, e.g., furlongs.

    outputLine = {
      'label': json['label'],
      'result': nf.formatImpl(input),
      'actual_options': options.toMapString(),
    };
  } catch (error, stacktrace) {
    // Handle type of the error
    outputLine = {
      'label': json['label'],
      'error': 'formatting error: $error',
      'stacktrace': stacktrace.toString(),
      'actual_options': options.toMapString(),
    };

    /// Uncomment the line below for easier debugging
    // rethrow;
  }
  return jsonEncode(outputLine);
}

List<String> _getUnsupportedSkeletonterms(
  List<String> skeletonTerms,
  bool doLogInput,
) {
  final unsupportedOptions = <String>[];

  // Check for skelection terms that are not supported
  for (var skelTerm in skeletonTerms) {
    if (doLogInput) {
      print('# SKEL_TERM: $skelTerm');
    }
    if (_unsupportedSkeletonTerms.contains(skelTerm)) {
      unsupportedOptions.add(skelTerm);
      if (doLogInput) {
        print('# UNSUPPORTED SKEL_TERM: $skelTerm');
      }
    }
  }
  return unsupportedOptions;
}

NumberFormatOptions _decimalPatternToOptions(
  String? pattern,
  String? rounding,
) {
  final numberFormatOptions =
      _patternsToOptions[pattern] ?? NumberFormatOptions.custom();
  if (rounding != null) {
    final roundingMode = RoundingMode.values.firstWhere(
      (mode) => mode.name == rounding,
    );
    return numberFormatOptions.copyWith(roundingMode: roundingMode);
  } else {
    //TODO: remove this halfEven default override, as soon as it is always passed in the numberformat args.
    return numberFormatOptions.copyWith(roundingMode: RoundingMode.halfEven);
  }
}

NumberFormatOptions _fromJson(Map<String, dynamic> options) {
  Unit? unit;
  if (options['unit'] != null) {
    unit = Unit.values
        .where((element) => element.jsName == options['unit'])
        .firstOrNull;
    if (unit == null) {
      throw ArgumentError('Unknown unit ${options['unit']}');
    }
  }
  final unitDisplay = UnitDisplay.values
      .where((element) => element.name == options['unitDisplay'])
      .firstOrNull;

  final currency = options['currency'];
  final currencyDisplay = CurrencyDisplay.values
      .where((element) => element.name == options['currencyDisplay'])
      .firstOrNull;
  final style = [
    DecimalStyle(),
    if (currency != null)
      CurrencyStyle(
        currency: currency,
        display: currencyDisplay ?? CurrencyDisplay.symbol,
        sign:
            CurrencySign.values.firstWhereOrNull(
              (element) => element.name == options['currencySign'] as String?,
            ) ??
            CurrencySign.standard,
      ),
    if (unit != null)
      UnitStyle(unit: unit, unitDisplay: unitDisplay ?? UnitDisplay.short),
  ].where((element) => element.name == options['style']).firstOrNull;

  final compactDisplay = CompactDisplay.values
      .where((element) => element.name == options['compactDisplay'])
      .firstOrNull;
  final notation = [
    CompactNotation(compactDisplay: compactDisplay ?? CompactDisplay.short),
    StandardNotation(),
    ScientificNotation(),
    EngineeringNotation(),
  ].where((element) => element.name == options['notation']).firstOrNull;
  final signDisplay = SignDisplay.values
      .where((element) => element.name == options['signDisplay'])
      .firstOrNull;
  final useGrouping = Grouping.values
      .where((element) => element.jsName == options['useGrouping'])
      .firstOrNull;
  final roundingMode = RoundingMode.values
      .where((element) => element.name == options['roundingMode'])
      .firstOrNull;
  final trailingZeroDisplay = TrailingZeroDisplay.values
      .where((element) => element.name == options['trailingZeroDisplay'])
      .firstOrNull;
  final minimumSignificantDigits = options['minimumSignificantDigits'] as int?;
  final maximumSignificantDigits = options['maximumSignificantDigits'] as int?;
  final roundingIncrement = options['roundingIncrement'] as int?;
  final roundingPriority =
      RoundingPriority.values
          .where((element) => element.name == options['roundingPriority'])
          .firstOrNull ??
      RoundingPriority.auto;
  final minimumFractionDigits = options['minimumFractionDigits'] as int?;
  final maximumFractionDigits = options['maximumFractionDigits'] as int?;

  Digits? digits;
  if ((minimumFractionDigits != null || maximumFractionDigits != null) &&
      (minimumSignificantDigits != null || maximumSignificantDigits != null)) {
    digits = Digits.withSignificantAndFractionDigits(
      maximumFractionDigits: maximumFractionDigits,
      maximumSignificantDigits: maximumSignificantDigits,
      minimumFractionDigits: minimumFractionDigits,
      minimumSignificantDigits: minimumSignificantDigits,
      roundingPriority: roundingPriority,
    );
  } else if (minimumFractionDigits != null || maximumFractionDigits != null) {
    digits = Digits.withFractionDigits(
      minimum: minimumFractionDigits,
      maximum: maximumFractionDigits,
      roundingIncrement: roundingIncrement,
    );
  } else if (minimumSignificantDigits != null ||
      maximumSignificantDigits != null) {
    digits = Digits.withSignificantDigits(
      minimum: minimumSignificantDigits,
      maximum: maximumSignificantDigits,
    );
  }

  return NumberFormatOptions.custom().copyWith(
    style: style,
    currency: currency,
    signDisplay: signDisplay,
    notation: notation,
    useGrouping: useGrouping,
    numberingSystem: NumberingSystem.values.firstWhereOrNull(
      (element) => element.jsName == options['numberingSystem'],
    ),
    roundingMode: roundingMode,
    trailingZeroDisplay: trailingZeroDisplay,
    minimumIntegerDigits: options['minimumIntegerDigits'],
    digits: digits,
  );
}

extension on NumberFormatOptions {
  Map<String, dynamic> toMapString() {
    return {
      'style': style.name,
      'currency': currency,
      'signDisplay': signDisplay.name,
      'notation': notation.name,
      'useGrouping': useGrouping.jsName,
      'numberingSystem': numberingSystem?.jsName,
      'roundingMode': roundingMode.name,
      'trailingZeroDisplay': trailingZeroDisplay.name,
      'minimumIntegerDigits': minimumIntegerDigits,
      'digits': {
        'fractionDigits': digits?.fractionDigits.toString(),
        'significantDigits': digits?.significantDigits.toString(),
        'roundingPriority': digits?.roundingPriority?.toString(),
        'roundingIncrement': digits?.roundingIncrement?.toString(),
      },
    };
  }

  NumberFormatOptions copyWith({
    FormatStyle? style,
    String? currency,
    SignDisplay? signDisplay,
    Notation? notation,
    Grouping? useGrouping,
    NumberingSystem? numberingSystem,
    RoundingMode? roundingMode,
    TrailingZeroDisplay? trailingZeroDisplay,
    int? minimumIntegerDigits,
    Digits? digits,
  }) => NumberFormatOptions.custom(
    style: style ?? this.style,
    currency: currency ?? this.currency,
    signDisplay: signDisplay ?? this.signDisplay,
    notation: notation ?? this.notation,
    useGrouping: useGrouping ?? this.useGrouping,
    numberingSystem: numberingSystem ?? this.numberingSystem,
    roundingMode: roundingMode ?? this.roundingMode,
    trailingZeroDisplay: trailingZeroDisplay ?? this.trailingZeroDisplay,
    minimumIntegerDigits: minimumIntegerDigits ?? this.minimumIntegerDigits,
    digits: digits ?? this.digits,
  );
}

// Copied from intl4x/lib/src/number_format/number_format_ecma.dart
/// Extension to provide a JavaScript-compatible name for the Unit enum.
extension on Unit {
  /// The JavaScript-compatible string representation of the unit.
  String get jsName => switch (this) {
    Unit.fluidOunce => 'fluid-ounce',
    Unit.scandinavianMile => 'mile-scandinavian',
    // Fallback to the enum's name for all other units (e.g., 'acre', 'bit',
    // 'byte').
    _ => name,
  };
}

// Copied from intl4x/lib/src/locale/locale.dart
extension NumberingSystemJsName on NumberingSystem {
  /// Returns the BCP 47/CLDR short name for the numbering system.
  String get jsName => switch (this) {
    NumberingSystem.arabic => 'arab',
    NumberingSystem.extendedarabicindic => 'arabext',
    NumberingSystem.balinese => 'bali',
    NumberingSystem.bangla => 'beng',
    NumberingSystem.devanagari => 'deva',
    NumberingSystem.fullwidth => 'fullwide',
    NumberingSystem.gujarati => 'gujr',
    NumberingSystem.gurmukhi => 'guru',
    NumberingSystem.hanjadecimal => 'hant',
    NumberingSystem.khmer => 'khmr',
    NumberingSystem.kannada => 'knda',
    NumberingSystem.lao => 'laoo',
    NumberingSystem.malayalam => 'mlym',
    NumberingSystem.mongolian => 'mong',
    NumberingSystem.myanmar => 'mymr',
    NumberingSystem.odia => 'orya',
    NumberingSystem.tamildecimal => 'taml',
    NumberingSystem.telugu => 'telu',
    NumberingSystem.thai => 'thai',
    NumberingSystem.tibetan => 'tibt',
    NumberingSystem.latin => 'latn',
    NumberingSystem.limbu => 'limb',
  };
}

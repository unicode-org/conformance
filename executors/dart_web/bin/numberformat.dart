import 'dart:convert';

import 'package:intl4x/ecma_policy.dart';
import 'package:intl4x/intl4x.dart';
import 'package:intl4x/number_format.dart';

final patternsToOptions = <String, NumberFormatOptions>{
  '0.0':
      NumberFormatOptions.custom(digits: Digits.withFractionDigits(minimum: 1)),
  '00': NumberFormatOptions.custom(
      digits: Digits.withSignificantDigits(minimum: 1)),
  '@@@': NumberFormatOptions.custom(
      digits: Digits.withSignificantDigits(minimum: 3)),
  '@@###': NumberFormatOptions.custom(
      digits: Digits.withSignificantDigits(minimum: 2, maximum: 5)),
  '0.0000E0': NumberFormatOptions.custom(
      notation: ScientificNotation(),
      digits: Digits.withFractionDigits(minimum: 4)),
};

// The nodejs version that first supported advance rounding options
const firstV3Version = 'v20.1.0';

enum NodeVersion {
  v3,
  preV3,
}

const unsupportedSkeletonTerms = [
  'scientific/+ee/sign-always',
  'decimal-always',
];

// Use this
const supportedOptionsByVersion = {
  NodeVersion.v3: [
    'compactDisplay',
    'currency',
    'currencyDisplay',
    'currencySign',
    'localeMatcher',
    'notation',
    'numberingSystem',
    'signDisplay',
    'style',
    'unit',
    'unitDisplay',
    'useGrouping',
    'roundingMode',
    'roundingPriority',
    'roundingIncrement',
    'trailingZeroDisplay',
    'minimumIntegerDigits',
    'minimumFractionDigits',
    'maximumFractionDigits',
    'minimumSignificantDigits',
    'maximumSignificantDigits'
  ],
  NodeVersion.preV3: [
    'compactDisplay',
    'currency',
    'currencyDisplay',
    'currencySign',
    'localeMatcher',
    'notation',
    'numberingSystem',
    'signDisplay',
    'style',
    'unit',
    'unitDisplay',
    'useGrouping',
    'roundingMode',
    'minimumIntegerDigits',
    'minimumFractionDigits',
    'maximumFractionDigits',
    'minimumSignificantDigits',
    'maximumSignificantDigits'
  ]
  // TODO: Add older version support.
};

String testDecimalFormat(
  String encoded, [
  bool doLogInput = false,
  String nodeVersion = '',
]) {
  final json = jsonDecode(encoded) as Map<String, dynamic>;
  final label = json['label'] as String?;
  final skeleton = json['skeleton'] as String?;
  final pattern = json['pattern'] as String?;
  final rounding = json['rounding'] as String?;
  var input =
      double.parse(json['input'] as String); // May be changed with some options

  final unsupportedOptions = <String>[];

  // If options are in the JSON, use them...
  NumberFormatOptions options;
  final jsonOptions = (json['options'] ?? {}) as Map<String, dynamic>;
  if (jsonOptions.isNotEmpty) {
    options = _fromJson(jsonOptions);
  } else {
    try {
      options = _decimalPatternToOptions(pattern, rounding);
    } catch (error) {
      // Some error - to return this message
      return jsonEncode({
        'error': 'Can\'t convert pattern',
        'label': label,
      });
    }
  }
  // Default maximumFractionDigits and rounding modes are set in test generation

  // Check each option for implementation.
  // Handle percent - input value is the basis of the actual percent
  // expected, e.g., input='0.25' should be interpreted '0.25%'
  if (options.style is PercentStyle) {
    input = input / 100.0;
  }

  // Handle scale in the skeleton
  List<String> skeletonTerms;
  if (skeleton != null) {
    skeletonTerms = skeleton.split(' '); // all the components
    if (doLogInput) {
      print('# SKEL: $skeletonTerms');
    }
    final scaleRegex = RegExp(r'/scale\/(\d+\.\d*)/');
    final matchScale = scaleRegex.firstMatch(skeleton);
    if (matchScale != null) {
      // Get the value and use it
      final scaleValue = double.parse(matchScale.group(1)!);
      input = input * scaleValue;
    }
  } else {
    skeletonTerms = [];
  }

  // Supported options depends on the nodejs version
  if (doLogInput) {
    print('#NNNN $nodeVersion');
  }
  List<String> versionSupportedOptions;
  if (nodeVersion.compareTo(firstV3Version) >= 0) {
    if (doLogInput) {
      print('#V3 !!!! $nodeVersion');
    }
    versionSupportedOptions = supportedOptionsByVersion[NodeVersion.v3]!;
  } else {
    if (doLogInput) {
      print('#pre_v3 !!!! $nodeVersion');
    }
    versionSupportedOptions = supportedOptionsByVersion[NodeVersion.preV3]!;
  }
  if (doLogInput) {
    print('#NNNN $versionSupportedOptions');
  }
  // Check for option items that are not supported
  for (var key in jsonOptions.keys) {
    if (!versionSupportedOptions.contains(key)) {
      unsupportedOptions.add('$key:${jsonOptions[key]}');
    }
  }

  // Check for skelection terms that are not supported
  for (var skelTerm in skeletonTerms) {
    if (doLogInput) {
      print('# SKEL_TERM: $skelTerm');
    }
    if (unsupportedSkeletonTerms.contains(skelTerm)) {
      unsupportedOptions.add(skelTerm);
      if (doLogInput) {
        print('# UNSUPPORTED SKEL_TERM: $skelTerm');
      }
    }
  }

  if (unsupportedOptions.isNotEmpty) {
    return jsonEncode({
      'label': label,
      'unsupported': 'unsupported_options',
      'error_detail': {'unsupported_options': unsupportedOptions}
    });
  }

  final testLocale = json['locale'] as String?;

  Intl intl;
  Map<String, dynamic> outputLine;
  try {
    if (testLocale != null) {
      intl = Intl(
        locale: Locale.parse(testLocale),
        ecmaPolicy: AlwaysEcma(),
      );
    } else {
      intl = Intl(
        locale: const Locale(language: 'und'),
        ecmaPolicy: AlwaysEcma(),
      );
    }
    final NumberFormat nf = intl.numberFormat(options);

    // TODO: Catch unsupported units, e.g., furlongs.

    outputLine = {
      'label': json['label'],
      'result': nf.format(input),
      'actual_options': options.toMapString(),
    };
  } catch (error) {
    if (error.toString().contains('furlong')) {
      // This is a special kind of unsupported.
      return jsonEncode({
        'label': label,
        'unsupported': 'unsupported_options',
        'error_detail': {'unsupported_options': error.toString()}
      });
    }
    // Handle type of the error
    outputLine = {
      'label': json['label'],
      'error': 'formatting error: $error',
      'actual_options': options.toMapString(),
    };

    /// Uncomment the line below for easier debugging
    // rethrow;
  }
  return jsonEncode(outputLine);
}

NumberFormatOptions _decimalPatternToOptions(
    String? pattern, String? rounding) {
  final numberFormatOptions =
      patternsToOptions[pattern] ?? NumberFormatOptions.custom();
  if (rounding != null) {
    final roundingMode =
        RoundingMode.values.firstWhere((mode) => mode.name == rounding);
    return numberFormatOptions.copyWith(roundingMode: roundingMode);
  } else {
    return numberFormatOptions;
  }
}

NumberFormatOptions _fromJson(Map<String, dynamic> options) {
  final unit = Unit.values
      .where((element) => element.jsName == options['unit'])
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
      ),
    if (unit != null) UnitStyle(unit: unit),
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
  final unitDisplay = UnitDisplay.values
      .where((element) => element.name == options['unitDisplay'])
      .firstOrNull;
  final signDisplay = SignDisplay.values
      .where((element) => element.name == options['signDisplay'])
      .firstOrNull;
  final localeMatcher = LocaleMatcher.values
      .where((element) => element.jsName == options['localeMatcher'])
      .firstOrNull;
  final useGrouping = Grouping.values
      .where((element) => element.jsName == options['useGrouping'].toString())
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
  final roundingPriority = RoundingPriority.values
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
    currencyDisplay: currencyDisplay,
    unit: unit,
    unitDisplay: unitDisplay,
    localeMatcher: localeMatcher,
    signDisplay: signDisplay,
    notation: notation,
    useGrouping: useGrouping,
    numberingSystem: options['numberingSystem'],
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
      'currencyDisplay': currencyDisplay?.toString(),
      'unit': unit?.jsName,
      'unitDisplay': unitDisplay?.toString(),
      'localeMatcher': localeMatcher.jsName,
      'signDisplay': signDisplay.name,
      'notation': notation.name,
      'useGrouping': useGrouping.jsName,
      'numberingSystem': numberingSystem?.toString(),
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
}

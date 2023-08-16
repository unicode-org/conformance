import 'dart:convert';

import 'package:intl4x/intl4x.dart';
import 'package:intl4x/number_format.dart';

final patternsToOptions = <String, NumberFormatOptions>{
  "0.0":
      NumberFormatOptions.custom(digits: Digits.withFractionDigits(minimum: 1)),
  "00": NumberFormatOptions.custom(
      digits: Digits.withSignificantDigits(minimum: 1)),
  "@@@": NumberFormatOptions.custom(
      digits: Digits.withSignificantDigits(minimum: 3)),
  "@@###": NumberFormatOptions.custom(
      digits: Digits.withSignificantDigits(minimum: 2, maximum: 5)),
  "0.0000E0": NumberFormatOptions.custom(
      notation: ScientificNotation(),
      digits: Digits.withFractionDigits(minimum: 4)),
};

// The nodejs version that first supported advance rounding options
const first_v3_version = 'v20.1.0';

enum NodeVersion {
  v3,
  preV3,
}

const unsupported_skeleton_terms = [
  "scientific/+ee/sign-always",
  "decimal-always",
];

const unsupported_rounding_modes = ["unnecessary"];

// Use this
const supported_options_by_version = {
  NodeVersion.v3: [
    "compactDisplay",
    "currency",
    "currencyDisplay",
    "currencySign",
    "localeMatcher",
    "notation",
    "numberingSystem",
    "signDisplay",
    "style",
    "unit",
    "unitDisplay",
    "useGrouping",
    "roundingMode",
    "roundingPriority",
    "roundingIncrement",
    "trailingZeroDisplay",
    "minimumIntegerDigits",
    "minimumFractionDigits",
    "maximumFractionDigits",
    "minimumSignificantDigits",
    "maximumSignificantDigits"
  ],
  NodeVersion.preV3: [
    "compactDisplay",
    "currency",
    "currencyDisplay",
    "currencySign",
    "localeMatcher",
    "notation",
    "numberingSystem",
    "signDisplay",
    "style",
    "unit",
    "unitDisplay",
    "useGrouping",
    "roundingMode",
    "minimumIntegerDigits",
    "minimumFractionDigits",
    "maximumFractionDigits",
    "minimumSignificantDigits",
    "maximumSignificantDigits"
  ]
  // TODO: Add older version support.
};

String testDecimalFormat(
  String encoded,
  bool doLogInput,
  String node_version,
) {
  final json = jsonDecode(encoded);
  final label = json['label'] as String?;
  final skeleton = json['skeleton'] as String?;
  final pattern = json['pattern'] as String?;
  final rounding = json['rounding'] as String?;
  var input =
      double.parse(json['input'] as String); // May be changed with some options

  var unsupported_options = [];

  // If options are in the JSON, use them...
  NumberFormatOptions options;
  var jsonOptions = json['options'] as Map<String, dynamic>;
  if (json.containsKey('options')) {
    options = fromJson(jsonOptions);
  } else {
    try {
      options = decimalPatternToOptions(pattern, rounding);
    } catch (error) {
      // Some error - to return this message
      return jsonEncode({
        'error': "Can't convert pattern",
        'label': label,
      });
    }
  }
  // Default maximumFractionDigits and rounding modes are set in test generation
  final roundingMode = options.roundingMode;

  // Check each option for implementation.
  // Handle percent - input value is the basis of the actual percent
  // expected, e.g., input='0.25' should be interpreted '0.25%'
  if (options.style is PercentStyle) {
    input = input / 100.0;
  }

  // Handle scale in the skeleton
  var skeleton_terms;
  if (skeleton != null) {
    skeleton_terms = skeleton.split(" "); // all the components
    if (doLogInput) {
      print("# SKEL: " + skeleton_terms);
    }
    final scale_regex = RegExp(r'/scale\/(\d+\.\d*)/');
    final match_scale = scale_regex.firstMatch(skeleton);
    if (match_scale != null) {
      // Get the value and use it
      final scale_value = double.parse(match_scale.group(1)!);
      input = input * scale_value;
    }
  }

  // Supported options depends on the nodejs version
  if (doLogInput) {
    print("#NNNN " + node_version);
  }
  List<String> version_supported_options;
  if (node_version.compareTo(first_v3_version) >= 0) {
    if (doLogInput) {
      print("#V3 !!!! " + node_version);
    }
    version_supported_options = supported_options_by_version[NodeVersion.v3]!;
  } else {
    if (doLogInput) {
      print("#pre_v3 !!!! " + node_version);
    }
    version_supported_options =
        supported_options_by_version[NodeVersion.preV3]!;
  }
  if (doLogInput) {
    print("#NNNN $version_supported_options");
  }
  // Check for option items that are not supported
  for (var key in jsonOptions.keys) {
    if (!version_supported_options.contains(key)) {
      unsupported_options.add((key + ":" + jsonOptions[key]));
    }
  }

  // Check for skelection terms that are not supported
  for (var skel_index in skeleton_terms) {
    final skel_term = skeleton_terms[skel_index];
    if (doLogInput) {
      print("# SKEL_TERM: " + skel_term);
    }
    if (unsupported_skeleton_terms.contains(skel_term)) {
      unsupported_options.add(skel_term);
      if (doLogInput) {
        print("# UNSUPPORTED SKEL_TERM: " + skel_term);
      }
    }
  }

  if (unsupported_rounding_modes.contains(roundingMode.name)) {
    unsupported_options.add(roundingMode.name);
  }
  if (unsupported_options.length > 0) {
    return jsonEncode({
      'label': label,
      "unsupported": "unsupported_options",
      "error_detail": {'unsupported_options': unsupported_options}
    });
  }

  var testLocale = json['locale'];

  NumberFormat nf;
  Map<String, dynamic> outputLine;
  try {
    if (testLocale) {
      nf = Intl(locale: testLocale).numberFormat(options);
    } else {
      nf = Intl(locale: Locale(language: 'und')).numberFormat(options);
    }

    var result = 'NOT IMPLEMENTED';
    result = nf.format(input);

    // TODO: Catch unsupported units, e.g., furlongs.
    // Formatting as JSON
    var resultString = result;

    outputLine = {
      "label": json['label'],
      "result": resultString,
      "actual_options": options
    };
  } catch (error) {
    if (error.toString().contains('furlong')) {
      // This is a special kind of unsupported.
      return jsonEncode({
        'label': label,
        "unsupported": "unsupported_options",
        "error_detail": {'unsupported_options': error.toString()}
      });
    }
    // Handle type of the error
    outputLine = {
      "label": json['label'],
      "error": "formatting error",
    };
    if (error is RangeError) {
      outputLine['error_detail'] = error.message;
      outputLine['actual_options'] = options;
    }
  }
  return jsonEncode(outputLine);
}

NumberFormatOptions decimalPatternToOptions(String? pattern, String? rounding) {
  final numberFormatOptions =
      patternsToOptions[pattern] ?? NumberFormatOptions.custom();
  if (rounding != null) {
    var roundingMode =
        RoundingMode.values.firstWhere((mode) => mode.name == rounding);
    return numberFormatOptions.copyWith(roundingMode: roundingMode);
  } else {
    return numberFormatOptions;
  }
}

NumberFormatOptions fromJson(Map<String, dynamic> options) {
  return NumberFormatOptions.custom();
}

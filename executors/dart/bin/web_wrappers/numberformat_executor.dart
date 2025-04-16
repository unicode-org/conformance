import 'dart:convert';

import 'package:dart_executor/numberformat.dart';

void main(List<String> args) {
  final loggingEnabled = bool.parse(args[2]);
  //just some call to not treeshake the function
  final encoded = args.first;
  final json = jsonDecode(encoded) as Map<String, dynamic>;
  final jsonOptions = (json['options'] ?? {}) as Map<String, dynamic>;
  final getUnsupportedOptionsForNode = _getUnsupportedOptionsForNode(
    jsonOptions,
    args[2],
    loggingEnabled,
  );
  testDecimalFormat(encoded, loggingEnabled, getUnsupportedOptionsForNode);
}

List<String> _getUnsupportedOptionsForNode(
  Map<String, dynamic> jsonOptions,
  String nodeVersion,
  bool doLogInput,
) {
  List<String> versionSupportedOptions;
  if (nodeVersion.compareTo(_firstV3Version) >= 0) {
    if (doLogInput) {
      print('#V3 !!!! $nodeVersion');
    }
    versionSupportedOptions = _supportedOptionsByVersion[NodeVersion.v3]!;
  } else {
    if (doLogInput) {
      print('#pre_v3 !!!! $nodeVersion');
    }
    versionSupportedOptions = _supportedOptionsByVersion[NodeVersion.preV3]!;
  }
  if (doLogInput) {
    print('#NNNN $versionSupportedOptions');
  }

  final unsupportedOptions = <String>[];
  // Check for option items that are not supported
  for (var key in jsonOptions.keys) {
    if (!versionSupportedOptions.contains(key)) {
      unsupportedOptions.add('$key:${jsonOptions[key]}');
    }
  }
  return unsupportedOptions;
}

// The nodejs version that first supported advance rounding options
const _firstV3Version = 'v20.1.0';

enum NodeVersion { v3, preV3 }

// Use this
const _supportedOptionsByVersion = {
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
    'maximumSignificantDigits',
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
    'maximumSignificantDigits',
  ],
  // TODO: Add older version support.
};

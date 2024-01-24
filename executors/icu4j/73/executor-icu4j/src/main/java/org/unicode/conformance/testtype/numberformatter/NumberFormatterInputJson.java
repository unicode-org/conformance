package org.unicode.conformance.testtype.numberformatter;

import java.util.Map;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class NumberFormatterInputJson implements ITestTypeInputJson {

  String label;

  String locale;

  String pattern;

  String skeleton;

  String input;

  String op;

  Map<NumberFormatterTestOptionKey, Object> options;
}

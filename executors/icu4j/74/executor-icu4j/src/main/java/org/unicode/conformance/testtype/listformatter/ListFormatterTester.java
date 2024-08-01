package org.unicode.conformance.testtype.listformatter;

import com.ibm.icu.util.ULocale;
import com.ibm.icu.text.ListFormatter.Type;
import com.ibm.icu.text.ListFormatter.Width;
import com.ibm.icu.text.ListFormatter;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;

import java.util.Collection;

import java.util.HashMap;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;
import org.unicode.conformance.testtype.numberformatter.NumberFormatterTestOptionKey;
import org.unicode.conformance.testtype.numberformatter.StyleVal;

public class ListFormatterTester implements ITestType {

  public static ListFormatterTester INSTANCE = new ListFormatterTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    ListFormatterInputJson result = new ListFormatterInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);

    java.util.Map<String,Object> input_options = (java.util.Map<String,Object>) inputMapData.get("options", null);

    result.list_type = ListFormatterType.getFromString(
        "" + input_options.get("list_type")
    );
    result.style = ListFormatterWidth.getFromString(
        "" + input_options.get("style")
    );

    result.input_list = (Collection<String>) inputMapData.get("input_list", null);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    ListFormatterInputJson input = (ListFormatterInputJson) inputJson;

    // partially construct output
    ListFormatterOutputJson output = (ListFormatterOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      output.result = getListFormatResultString(input);
    } catch (Exception e) {
      output.error = e.getMessage();
      output.error_message = e.getMessage();
      return output;
    }

    // If we get here, it's a pass/fail result (supported options and no runtime errors/exceptions)
    return output;
  }

  @Override
  public ITestTypeOutputJson getDefaultOutputJson() {
    return new ListFormatterOutputJson();
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    ListFormatterOutputJson output = (ListFormatterOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String,Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((ListFormatterOutputJson) outputJson);
  }

  public String getListFormatResultString(ListFormatterInputJson input) {
    ListFormatter.Type list_type;
    ListFormatter.Width list_width;
    ULocale locale = ULocale.forLanguageTag(input.locale);

    switch (input.list_type) {
      case DISJUNCTION: list_type = Type.OR;
        break;
      case UNIT: list_type = Type.UNITS;
        break;
      default:
      case CONJUNCTION: list_type = Type.AND;
        break;
    }

    switch (input.style) {
      case NARROW: list_width = Width.NARROW;
        break;
      case SHORT: list_width = Width.SHORT;
        break;
      default:
      case LONG: list_width = Width.WIDE;
        break;
    }

    ListFormatter lf = ListFormatter.getInstance(locale, list_type, list_width);

    return  lf.format(input.input_list);
  }
}

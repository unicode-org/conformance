package org.unicode.conformance.testtype.listformatter;

import com.ibm.icu.util.ULocale;
import com.ibm.icu.text.ListFormatter.Type;
import com.ibm.icu.text.ListFormatter.Width;
import com.ibm.icu.text.ListFormatter;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;

import java.util.Collection;

import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class ListFormatterTester implements ITestType {

  public static ListFormatterTester INSTANCE = new ListFormatterTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    ListFormatterInputJson result = new ListFormatterInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);

    java.util.Map<String, Object> inputOptions = (java.util.Map<String, Object>) inputMapData.get(
        "options", null);

    result.listType = ListFormatterType.getFromString(
        "" + inputOptions.get("list_type")
    );
    result.style = ListFormatterWidth.getFromString(
        "" + inputOptions.get("style")
    );

    result.inputList = (Collection<String>) inputMapData.get("input_list", null);

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
    return new io.lacuna.bifurcan.Map<String, Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((ListFormatterOutputJson) outputJson);
  }

  public String getListFormatResultString(ListFormatterInputJson input) {
    ListFormatter.Type listType;
    ListFormatter.Width listWidth;
    ULocale locale = ULocale.forLanguageTag(input.locale);

    switch (input.listType) {
      case DISJUNCTION:
        listType = Type.OR;
        break;
      case UNIT:
        listType = Type.UNITS;
        break;
      default:
      case CONJUNCTION:
        listType = Type.AND;
        break;
    }

    switch (input.style) {
      case NARROW:
        listWidth = Width.NARROW;
        break;
      case SHORT:
        listWidth = Width.SHORT;
        break;
      default:
      case LONG:
        listWidth = Width.WIDE;
        break;
    }

    ListFormatter lf = ListFormatter.getInstance(locale, listType, listWidth);

    return lf.format(input.inputList);
  }
}

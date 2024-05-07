package org.unicode.conformance.testtype.messageformat2;

import com.ibm.icu.message2.MessageFormatter;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;
public class MessageFormatTester implements ITestType {

  public static MessageFormatTester INSTANCE = new MessageFormatTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    MessageFormatInputJson result = new MessageFormatInputJson();

    result.test_type = (String) inputMapData.get("test_type", null);
    result.label = (String) inputMapData.get("label", null);

    result.test_subtype = (MFTestSubType) inputMapData.get("test_subtype", null);
    result.locale = (String) inputMapData.get("locale", null);
    result.pattern = (String) inputMapData.get("pattern", null);
    result.test_description = (String) inputMapData.get("test_description", null);
    result.inputs = (List<MFInputArg>) inputMapData.get("inputs", null);
    result.verify = (String) inputMapData.get("verify", null);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    MessageFormatInputJson input = (MessageFormatInputJson) inputJson;

    // partially construct output
    MessageFormatOutputJson output = (MessageFormatOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      String messageFormatResult = getFormattedMessage(input);
      output.verify = messageFormatResult;
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
    return new MessageFormatOutputJson();
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    MessageFormatOutputJson output = (MessageFormatOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String,Object>()
        .put("label", output.label)
        .put("verify", output.verify);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((MessageFormatOutputJson) outputJson);
  }

  public String getFormattedMessage(MessageFormatInputJson input) {
    final Locale locale = Locale.forLanguageTag(input.locale);
    java.util.Map arguments = new HashMap<String,Object>();
    for (MFInputArg arg : input.inputs) {
      arguments.put(arg.name, arg.value);
    }

    MessageFormatter formatter = MessageFormatter.builder()
        .setPattern(input.pattern)
        .setLocale(locale)
        .build();

    return formatter.formatToString(arguments);
  }
}

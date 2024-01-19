package org.unicode.conformance.testtype.numberformatter;

import io.lacuna.bifurcan.Set;

public class RoundingIncrementUtil {
  private static final Set<Integer> validVals = Set.of(
      1,
      2,
      5,
      10,
      20,
      25,
      50,
      100,
      200,
      250,
      500,
      1000,
      2000,
      2500,
      5000
  );

  public static boolean isValidVal(int n) {
    return validVals.contains(n);
  }

}

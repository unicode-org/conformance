package org.unicode.conformance.testtype.segmenter;

public enum SegmenterType {
  CONJUNCTION,
  DISJUNCTION,
  UNIT;

  public static SegmenterType DEFAULT = CONJUNCTION;

  public static SegmenterType getFromString(String s) {
    try {
      return SegmenterType.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}

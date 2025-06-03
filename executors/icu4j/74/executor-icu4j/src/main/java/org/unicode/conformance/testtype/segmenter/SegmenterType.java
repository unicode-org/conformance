package org.unicode.conformance.testtype.segmenter;

public enum SegmenterType {
  GRAPHEME_CLUSTER,
  WORD,
  SENTENCE,
  LINE;

  public static SegmenterType DEFAULT = GRAPHEME_CLUSTER;

  public static SegmenterType getFromString(String s) {
    try {
      return SegmenterType.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}

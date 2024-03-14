package org.unicode.conformance.testtype.numberformatter;

public enum NuVal {
  NONE,  // a fake value to use as default
  adlm,
  ahom,
  arab,
  arabext,
  bali,
  beng,
  bhks,
  brah,
  cakm,
  cham,
  deva,
  diak,
  fullwide,
  gong,
  gonm,
  gujr,
  guru,
  hanidec,
  hmng,
  hmnp,
  java,
  kali,
  khmr,
  knda,
  lana,
  lanatham,
  laoo,
  latn,
  lepc,
  limb,
  mathbold,
  mathdbl,
  mathmono,
  mathsanb,
  mathsans,
  mlym,
  modi,
  mong,
  mroo,
  mtei,
  mymr,
  mymrshan,
  mymrtlng,
  newa,
  nkoo,
  olck,
  orya,
  osma,
  rohg,
  saur,
  segment,
  shrd,
  sind,
  sinh,
  sora,
  sund,
  takr,
  talu,
  tamldec,
  telu,
  thai,
  tibt,
  tirh,
  vaii,
  wara,
  wcho;

  public static NuVal DEFAULT = NONE;

  public static NuVal getFromString(String s) {
    try {
      return NuVal.valueOf(s);
    } catch (Exception e) {
      return DEFAULT;
    }
  }
}

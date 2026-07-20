import 'likely_subtags_native.dart'
    if (dart.library.js_interop) 'likely_subtags_web.dart';

String testLikelySubtags(String jsonEncoded) => testLikelySubtagsImpl(jsonEncoded);

import 'package:dart_executor/numberformat.dart';

void main(List<String> args) {
  //just some call to not treeshake the function
  testDecimalFormat(args[2], bool.parse(args.first), args.last);
}

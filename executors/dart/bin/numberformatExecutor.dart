import 'numberformat.dart';

void main(List<String> args) {
  //just some call to not treeshake the function
  testDecimalFormat(args.first, bool.parse(args[2]), args[3]);
}

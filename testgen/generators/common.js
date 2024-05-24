
function sample_tests(all_tests, run_limit) {
  // Gets a sampling of the data based on total and the expected number.

  if (run_limit < 0 || all_tests.length <= run_limit) {
    return all_tests;
  }

  let size_all = all_tests.length;
  let increment = Math.floor(size_all / run_limit);
  let samples = [];
  for (let index = 0; index < size_all; index += increment) {
    samples.push(all_tests[index]);
  }
  return samples;
}

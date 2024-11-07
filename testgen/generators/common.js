// Common functions for generation of test data from NodeJS

function sample_tests(all_tests, run_limit) {
  // Gets a sampling of the data based on total and the expected number.

  if (run_limit < 0 || all_tests.length <= run_limit) {
    return all_tests;
  }

  const label_increment = Math.floor(all_tests.length / run_limit);

  return samples = all_tests.filter((e, i) => i % label_increment == 0);
}

module.exports = {sample_tests};

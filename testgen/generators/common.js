// Common functions for generation of test data from NodeJS

// Globals to set increment and keep track of total generated.
let label_increment = 1;
let max_count = -1;
let added_count = 0;

const debug = false;

function sample_tests(all_tests, run_limit) {
  // Gets a sampling of the data based on total and the expected number.

  if (run_limit < 0 || all_tests.length <= run_limit) {
    return all_tests;
  }

  let size_all = all_tests.length;
  label_increment = Math.floor(size_all / run_limit);
  max_count = run_limit;
  added_count = 0;

  if (debug) {
    console.log('COMMON: ', size_all, ' increment: ', label_increment,
                ' max_count: ', max_count);
  }

  let samples = all_tests.filter(filter_every_nth);
  if (debug) {
    console.debug('  COMMON results: ', samples.length);
    console.debug('  COMMON results: ', samples);
  }
  return samples;
}

function filter_every_nth(test, index) {
  if (added_count >= max_count) {
    return false;
  }
  const add_this_one = ((index % label_increment) == 0);
  if (add_this_one) {
    added_count += 1;
  }
  return add_this_one
}

module.exports = {sample_tests};

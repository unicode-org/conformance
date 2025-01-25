// Adds a hex hash code based on the test without the label item.

const crypto = require('crypto');

function remove_none(obj) {
  // Recursively removes all null items
  if (typeof obj !== "object") {
    return obj;
  }
  const result = new obj.constructor;
  const entries = Object.entries(obj);
  entries.sort();
  for (const [key, value] of entries) {
    if (value !== null) {
      result[key] = remove_none(value);
    }
  }
  return result;
}

function generate_hash_for_test(test_case) {
  // Computes a 32 byte hex hash code for the test case
  // Note that the test case should not include 'label'.

  obj = remove_none(test_case);
  json_str = JSON.stringify(obj);

  const hasher = crypto.createHash("sha1");
  hasher.update(json_str, "utf-8");

  test_case['hexhash'] = hasher.digest("hex");
}

module.exports = {generate_hash_for_test};

var tools = require('./numberformatDart');
// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
module.exports = {
    testDecimalFormat: function (json) {
        return JSON.parse(tools.testDecimalFormat(JSON.stringify(json)));
    }
};

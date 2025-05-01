var tools = require('./collatorDart');
// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
module.exports = {
    testCollation: function (json) {
        return JSON.parse(tools.testCollation(JSON.stringify(json)));
    }
};

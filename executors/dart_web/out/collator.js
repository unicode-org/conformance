var tools = require('./collatorDart');
// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
module.exports = {
    testCollationShort: function (json) {
        let res = tools.testCollationShort(JSON.stringify(json));
        return JSON.parse(res);
    }
};

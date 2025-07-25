var tools = require('./datetimeformatDart');
// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
module.exports = {
    testDateTimeFmt: function (json, shouldLog, version) {
        return JSON.parse(tools.testDateTimeFmt(JSON.stringify(json), shouldLog, version));
    }
};

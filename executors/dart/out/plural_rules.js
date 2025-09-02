var tools = require('./plural_rulesDart');

module.exports = {
    testPluralRules: function (json) {
        return JSON.parse(tools.testPluralRules(JSON.stringify(json)));
    }
};

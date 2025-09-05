var tools = require('./lang_namesDart');

module.exports = {
    testLangNames: function (json) {
        return JSON.parse(tools.testLangNames(JSON.stringify(json)));
    }
};

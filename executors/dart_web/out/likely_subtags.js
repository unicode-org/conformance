var tools = require('./likely_subtagsDart');

module.exports = {
    testLikelySubtags: function (json) {
        return JSON.parse(tools.testLikelySubtags(JSON.stringify(json)));
    }
};

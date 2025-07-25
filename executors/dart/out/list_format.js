var tools = require('./list_formatDart');

module.exports = {
    testListFmt: function (json) {
        return JSON.parse(tools.testListFmt(JSON.stringify(json)));
    }
};

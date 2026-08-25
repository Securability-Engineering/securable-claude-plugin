const { execFile } = require("child_process");

function convert(filename) {
  execFile("convert", [filename, "out.png"], () => {});
}

module.exports = { convert };

const { exec } = require("child_process");

function convert(filename) {
  exec(`convert ${filename} out.png`, () => {});
}

module.exports = { convert };

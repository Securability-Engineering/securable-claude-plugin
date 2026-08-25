const jwt = require("jsonwebtoken");

function auth(token, secret) {
  return jwt.verify(token, secret);
}

module.exports = { auth };

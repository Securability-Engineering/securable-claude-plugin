const jwt = require("jsonwebtoken");

function auth(token, secret) {
  return jwt.verify(token, secret, { algorithms: ["HS256"], audience: "api", issuer: "auth-service" });
}

module.exports = { auth };

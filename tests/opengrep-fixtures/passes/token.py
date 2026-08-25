import jwt


def parse(token, key):
    return jwt.decode(token, key, algorithms=["RS256"], audience="api", issuer="https://issuer")

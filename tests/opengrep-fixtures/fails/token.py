import jwt


def parse(token, key):
    return jwt.decode(token, key)

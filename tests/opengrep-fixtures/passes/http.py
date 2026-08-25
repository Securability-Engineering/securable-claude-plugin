import requests


def fetch(url):
    return requests.get(url, timeout=(3, 10))

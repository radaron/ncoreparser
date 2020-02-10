from ncoreparser.client import Client
from ncoreparser.errors import NcoreConnectionError, NcoreCredentialError
from ncoreparser.data import URLs
from os import path, environ
import requests
import pytest
from _pytest.monkeypatch import monkeypatch
import json


cred = {}


class PostDummy:
    url = URLs.INDEX.value

class DummyCookies:
    def clear(self):
        pass

class RequestPostConError:
    def __init__(self):
        self.cookies = DummyCookies()

    def post(self, *args, **kwargs):
        raise Exception("")


@pytest.fixture(scope="session", autouse=True)
def collect_cred():
    global cred
    credentials = path.join(path.dirname(__file__), "cred.json")
    with open(credentials) as fh:
        cred = json.load(fh)
    yield


def test_credentials():
    Client(cred["username"], cred["password"])


def test_invalid_credentials():
    with pytest.raises(NcoreCredentialError):
        Client("Invalid_username", "Invalid_password")

def test_connection_error(monkeypatch):
    
    def mock_requests():
        return RequestPostConError()

    monkeypatch.setattr(requests, "session", mock_requests)
    
    with pytest.raises(NcoreConnectionError):
        Client(cred["username"], cred["password"])

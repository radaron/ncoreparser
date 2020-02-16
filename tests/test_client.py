from ncoreparser.client import Client
from ncoreparser.error import NcoreConnectionError, NcoreCredentialError
from ncoreparser.data import URLs
import requests
import pytest


class PostDummy:
    url = URLs.INDEX.value


class DummyCookies:
    def clear(self):
        pass


class DummyRequestUrl:
    def __init__(self, type):
        self.type = type
        if self.type == "bad":
            self.url = URLs.LOGIN.value
        elif self.type == "ok":
            self.url = URLs.INDEX.value


class RequestPost:
    def __init__(self, type):
        self.cookies = DummyCookies()
        self.type = type

    def post(self, *args, **kwargs):
        if self.type == "exception":
            raise Exception("")
        else:
            return DummyRequestUrl(self.type)

    def close(self):
        pass


"""
@pytest.fixture(scope="session", autouse=True)
def collect_cred():
    yield
"""


def test_credentials(monkeypatch):
    def mock_requests():
        return RequestPost("ok")

    monkeypatch.setattr(requests, "session", mock_requests)
    Client("username", "password")


def test_invalid_credentials(monkeypatch):
    def mock_requests():
        return RequestPost("bad")

    monkeypatch.setattr(requests, "session", mock_requests)
    with pytest.raises(NcoreCredentialError):
        Client("Invalid_username", "Invalid_password")


def test_connection_error(monkeypatch):
    def mock_requests():
        return RequestPost("exception")

    monkeypatch.setattr(requests, "session", mock_requests)

    with pytest.raises(NcoreConnectionError):
        Client("username", "password")

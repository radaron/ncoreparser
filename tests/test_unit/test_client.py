from unittest.mock import MagicMock
from ncoreparser.client import Client
from ncoreparser.error import NcoreConnectionError, NcoreCredentialError
from ncoreparser.data import URLs
import httpx
import pytest


class TestClient:

    def test_credentials(self, monkeypatch):
        client_stub = MagicMock()
        client_stub.return_value.post.return_value.url = URLs.INDEX.value

        monkeypatch.setattr(httpx, "Client", client_stub)
        c = Client()
        c.login("username", "password")

    def test_credentials_con_error(self, monkeypatch):
        client_stub = MagicMock()
        client_stub.return_value.post.side_effect = Exception()

        monkeypatch.setattr(httpx, "Client", client_stub)
        with pytest.raises(NcoreConnectionError):
            c = Client()
            c.login("username", "password")

    def test_invalid_credentials(self, monkeypatch):
        client_stub = MagicMock()
        client_stub.return_value.post.return_value.url = URLs.LOGIN.value

        monkeypatch.setattr(client_stub, "Client", client_stub)
        with pytest.raises(NcoreCredentialError):
            c = Client()
            c.login("username", "password")

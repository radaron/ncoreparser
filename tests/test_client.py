from unittest.mock import MagicMock

from ncoreparser.client import Client
from ncoreparser.error import NcoreConnectionError, NcoreCredentialError
from ncoreparser.data import URLs
import requests
import pytest

class TestClient:
    
    def test_credentials(self, monkeypatch):
        session = MagicMock()
        session.return_value.post.return_value.url = URLs.INDEX.value

        monkeypatch.setattr(requests, "session", session)
        Client("username", "password")

    def test_credentials_con_error(self, monkeypatch):
        session = MagicMock()
        session.return_value.post.side_effect = Exception()

        monkeypatch.setattr(requests, "session", session)
        with pytest.raises(NcoreConnectionError):
            Client("username", "password")

    def test_invalid_credentials(self, monkeypatch):
        session = MagicMock()
        session.return_value.post.return_value.url = URLs.LOGIN.value
        
        monkeypatch.setattr(requests, "session", session)
        with pytest.raises(NcoreCredentialError):
            Client("Invalid_username", "Invalid_password")
        session.return_value.close.assert_called_once()

"""Unit tests for the request timeout, run against a stubbed transport."""

from types import SimpleNamespace
import pytest
import requests
from cashctrl_api import CashCtrlClient
from cashctrl_api.constants import REQUEST_TIMEOUT


def test_request_carries_a_timeout(monkeypatch):
    calls = []

    def answer(method, url, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status_code=200)

    monkeypatch.setattr("cashctrl_api.client.request", answer)
    CashCtrlClient("org", "key").request("GET", "person/list.json")
    assert calls[0]["timeout"] == REQUEST_TIMEOUT


def test_unanswered_request_names_the_endpoint_without_a_retry(monkeypatch):
    calls = []

    def hang(method, url, **kwargs):
        calls.append(url)
        raise requests.exceptions.ReadTimeout("Read timed out.")

    monkeypatch.setattr("cashctrl_api.client.request", hang)
    with pytest.raises(requests.exceptions.ReadTimeout,
                       match="did not answer GET https://org.cashctrl.com/api/v1/person/list.json"):
        CashCtrlClient("org", "key").request("GET", "person/list.json")
    assert len(calls) == 1

"""Tests for shared components."""
import asyncio
from unittest.mock import patch, MagicMock

import pytest


class TestBaseClient:
    def test_init_reads_env(self):
        with patch.dict("os.environ", {"TEST_HOST": "example.com", "TEST_KEY": "secret"}):
            from src.common.client import BaseClient
            client = BaseClient("TEST_HOST", "TEST_KEY")
            assert client.host == "example.com"
            assert client.api_key == "secret"

    def test_headers_include_auth(self):
        with patch.dict("os.environ", {"TEST_HOST": "x", "TEST_KEY": "mytoken"}):
            from src.common.client import BaseClient
            client = BaseClient("TEST_HOST", "TEST_KEY")
            headers = client._headers()
            assert headers["Authorization"] == "Bearer mytoken"

    def test_query_dispatches_to_method(self):
        """query() should call a method named after the operation."""
        from src.common.client import BaseClient
        client = BaseClient("X", "Y")
        # Add a fake operation method
        client.test_op = MagicMock(return_value={"data": [1, 2, 3]})
        result = asyncio.get_event_loop().run_until_complete(
            client.query("test_op", {"foo": "bar"})
        )
        client.test_op.assert_called_once_with({"foo": "bar"})
        assert result == {"data": [1, 2, 3]}

    def test_query_returns_error_for_unknown_op(self):
        """query() should return an error dict for missing operations."""
        from src.common.client import BaseClient
        client = BaseClient("X", "Y")
        result = asyncio.get_event_loop().run_until_complete(
            client.query("nonexistent_op", {})
        )
        assert "error" in result
        assert "not implemented" in result["error"]

    def test_query_handles_http_error(self):
        """query() should catch requests.HTTPError and return error dict."""
        import requests
        from src.common.client import BaseClient
        client = BaseClient("X", "Y")

        def bad_op(params):
            resp = MagicMock()
            resp.status_code = 404
            resp.text = "Not Found"
            raise requests.HTTPError(response=resp)

        client.bad_op = bad_op
        result = asyncio.get_event_loop().run_until_complete(
            client.query("bad_op", {})
        )
        assert "error" in result
        assert "404" in result["error"]

    def test_query_handles_connection_error(self):
        """query() should catch ConnectionError and return error dict."""
        import requests
        from src.common.client import BaseClient
        client = BaseClient("X", "Y")

        def conn_fail(params):
            raise requests.ConnectionError("refused")

        client.conn_fail = conn_fail
        result = asyncio.get_event_loop().run_until_complete(
            client.query("conn_fail", {})
        )
        assert "error" in result
        assert "Connection failed" in result["error"]


class TestAnsibleBridge:
    def test_init(self):
        from src.common.bridge import AnsibleBridge
        bridge = AnsibleBridge("stevefulme1.elastic")
        assert bridge.collection == "stevefulme1.elastic"

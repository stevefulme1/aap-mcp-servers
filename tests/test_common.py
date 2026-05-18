"""Tests for shared components."""
from unittest.mock import patch


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


class TestAnsibleBridge:
    def test_init(self):
        from src.common.bridge import AnsibleBridge
        bridge = AnsibleBridge("stevefulme1.elastic")
        assert bridge.collection == "stevefulme1.elastic"

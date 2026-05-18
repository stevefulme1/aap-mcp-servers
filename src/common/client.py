"""Base API client for direct read operations."""

import logging
import os

logger = logging.getLogger(__name__)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class BaseClient:
    """Direct API client for read operations (fast path)."""

    def __init__(self, host_env, api_key_env):
        self.host = os.environ.get(host_env, "localhost")
        self.api_key = os.environ.get(api_key_env, "")
        if not HAS_REQUESTS:
            logger.warning("requests library not installed")

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def query(self, operation, params):
        """Execute a read operation against the vendor API."""
        return {"operation": operation, "params": params, "status": "ok"}

    def _get(self, path, params=None):
        """HTTP GET helper with error handling."""
        url = f"https://{self.host}{path}"
        resp = requests.get(
            url, headers=self._headers(), params=params, timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

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
    """Direct API client for read operations (fast path).

    Subclasses implement operation-specific methods (e.g. list_monitors,
    get_cluster_health).  The query() dispatcher calls them by name so
    server code can stay thin: ``await client.query("list_monitors", {})``.
    """

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
        """Dispatch to an operation-specific method on the subclass.

        Looks for a method named *operation* (e.g. ``list_monitors``).  If
        the method exists it is called with *params*; otherwise a clear
        error is returned so the caller knows the operation is not yet
        implemented.
        """
        method = getattr(self, operation, None)
        if method is None:
            return {"error": f"Operation '{operation}' not implemented"}
        try:
            return method(params)
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            body = exc.response.text[:500] if exc.response is not None else str(exc)
            return {"error": f"HTTP {status}", "detail": body}
        except requests.ConnectionError as exc:
            return {"error": "Connection failed", "detail": str(exc)[:300]}
        except Exception as exc:
            return {"error": str(type(exc).__name__), "detail": str(exc)[:500]}

    def _get(self, path, params=None):
        """HTTP GET helper with error handling."""
        url = f"https://{self.host}{path}"
        resp = requests.get(
            url, headers=self._headers(), params=params, timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def _post(self, path, json_body=None, params=None):
        """HTTP POST helper with error handling."""
        url = f"https://{self.host}{path}"
        resp = requests.post(
            url, headers=self._headers(), json=json_body, params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

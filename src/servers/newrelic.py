"""MCP Server for New Relic observability platform."""

import asyncio
import json
import logging
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge

logger = logging.getLogger(__name__)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


async def read_op(client, operation, params):
    """Execute a read operation (direct API)."""
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    """Execute a write operation (through Ansible)."""
    return await runner.execute(operation, params)


class NewRelicClient(BaseClient):
    """Direct API client for New Relic.

    Uses API-Key header for NerdGraph (GraphQL) and REST v2 endpoints.
    GraphQL: https://api.newrelic.com/graphql
    REST v2: https://api.newrelic.com/v2
    """

    def __init__(self):
        self.host = os.environ.get("NEWRELIC_HOST", "api.newrelic.com")
        self.api_key = os.environ.get("NEWRELIC_API_KEY", "")
        self.account_id = os.environ.get("NEWRELIC_ACCOUNT_ID", "")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "API-Key": self.api_key,
        }

    def _nerdgraph(self, query, variables=None):
        """Execute a NerdGraph (GraphQL) query."""
        url = f"https://{self.host}/graphql"
        body = {"query": query}
        if variables:
            body["variables"] = variables
        resp = requests.post(url, headers=self._headers(), json=body, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # -- read operations --

    def nrql_query(self, params):
        """Run a NRQL query via NerdGraph."""
        nrql = params.get("nrql", "SELECT count(*) FROM Transaction SINCE 1 hour ago")
        account = params.get("account_id", self.account_id)
        query = """
        {
          actor {
            account(id: %s) {
              nrql(query: "%s") {
                results
              }
            }
          }
        }
        """ % (account, nrql.replace('"', '\\"'))
        return self._nerdgraph(query)

    def list_alert_policies(self, params):
        """List alert policies via NerdGraph."""
        account = params.get("account_id", self.account_id)
        query = """
        {
          actor {
            account(id: %s) {
              alerts {
                policiesSearch {
                  policies { id name }
                }
              }
            }
          }
        }
        """ % account
        return self._nerdgraph(query)

    def get_alert_violations(self, params):
        """Get open alert violations via REST v2."""
        return self._get("/v2/alerts_violations.json", params={"only_open": "true"})

    def list_dashboards(self, params):
        """List dashboards via NerdGraph entity search."""
        query = """
        {
          actor {
            entitySearch(query: "type = 'DASHBOARD'") {
              results { entities { guid name } }
            }
          }
        }
        """
        return self._nerdgraph(query)

    def get_entity_details(self, params):
        """Get entity details by GUID."""
        guid = params.get("guid", "")
        query = """
        {
          actor {
            entity(guid: "%s") {
              name type domain tags { key values }
            }
          }
        }
        """ % guid
        return self._nerdgraph(query)

    def list_synthetics(self, params):
        """List Synthetic monitors via NerdGraph."""
        query = """
        {
          actor {
            entitySearch(query: "type = 'MONITOR'") {
              results { entities { guid name } }
            }
          }
        }
        """
        return self._nerdgraph(query)

    def get_sli_status(self, params):
        """Get SLI/SLO status via NerdGraph."""
        account = params.get("account_id", self.account_id)
        query = """
        {
          actor {
            account(id: %s) {
              nrql(query: "SELECT percentage(count(*), WHERE error IS false) FROM Transaction SINCE 1 day ago") {
                results
              }
            }
          }
        }
        """ % account
        return self._nerdgraph(query)

    def list_workloads(self, params):
        """List workloads via NerdGraph."""
        account = params.get("account_id", self.account_id)
        query = """
        {
          actor {
            account(id: %s) {
              workload {
                collections { id name permalink }
              }
            }
          }
        }
        """ % account
        return self._nerdgraph(query)

    def get_apm_summary(self, params):
        """Get APM application summary via REST v2."""
        return self._get("/v2/applications.json")

    def get_infra_hosts(self, params):
        """List infrastructure hosts via NerdGraph entity search."""
        query = """
        {
          actor {
            entitySearch(query: "type = 'HOST'") {
              results { entities { guid name tags { key values } } }
            }
          }
        }
        """
        return self._nerdgraph(query)


def create_newrelic_server():
    """Create and configure the MCP server."""
    server = Server("mcp-newrelic")
    client = NewRelicClient()
    runner = AnsibleBridge("stevefulme1.newrelic")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="nrql_query",
                description="Run NRQL query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "nrql": {"type": "string", "description": "NRQL query string"},
                        "account_id": {"type": "string", "description": "New Relic account ID (uses env default if omitted)"},
                    },
                    "required": ["nrql"],
                },
            ),
            Tool(
                name="list_alert_policies",
                description="List alert policies",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "account_id": {"type": "string"},
                    },
                },
            ),
            Tool(name="get_alert_violations", description="Get open alert violations", inputSchema={"type": "object"}),
            Tool(name="list_dashboards", description="List dashboards", inputSchema={"type": "object"}),
            Tool(
                name="get_entity_details",
                description="Get entity details by GUID",
                inputSchema={
                    "type": "object",
                    "properties": {"guid": {"type": "string", "description": "Entity GUID"}},
                    "required": ["guid"],
                },
            ),
            Tool(name="list_synthetics", description="List Synthetic monitors", inputSchema={"type": "object"}),
            Tool(name="get_sli_status", description="Get SLI/SLO status", inputSchema={"type": "object"}),
            Tool(name="list_workloads", description="List workloads", inputSchema={"type": "object"}),
            Tool(name="get_apm_summary", description="Get APM summary", inputSchema={"type": "object"}),
            Tool(name="get_infra_hosts", description="List infrastructure hosts", inputSchema={"type": "object"}),
            Tool(
                name="create_alert_policy",
                description="Create alert policy (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "incident_preference": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_alert_condition",
                description="Create alert condition (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"policy_id": {"type": "string"}, "name": {"type": "string"}, "type": {"type": "string"}},
                    "required": ["policy_id", "name"],
                },
            ),
            Tool(
                name="create_dashboard",
                description="Create dashboard (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_synthetic_monitor",
                description="Create Synthetic monitor (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "uri": {"type": "string"}, "type": {"type": "string"}},
                    "required": ["name", "uri"],
                },
            ),
            Tool(
                name="create_workload",
                description="Create workload (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="tag_entity",
                description="Tag an entity (via Ansible)",
                inputSchema={
                    "type": "object",
                    "properties": {"guid": {"type": "string"}, "tags": {"type": "object"}},
                    "required": ["guid", "tags"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "nrql_query", "list_alert_policies", "get_alert_violations",
            "list_dashboards", "get_entity_details", "list_synthetics",
            "get_sli_status", "list_workloads", "get_apm_summary",
            "get_infra_hosts",
        }
        write_tools = {
            "create_alert_policy", "create_alert_condition", "create_dashboard",
            "create_synthetic_monitor", "create_workload", "tag_entity",
        }
        if name in read_tools:
            result = await read_op(client, name, arguments)
        elif name in write_tools:
            result = await write_op(runner, name, arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    return server


def main():
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_newrelic_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()

"""MCP Server for Extreme Networks (ExtremeCloud IQ REST API)."""

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
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class ExtremeClient(BaseClient):
    """Direct API client for Extreme Networks.

    Uses Bearer token for ExtremeCloud IQ.
    Base URL: https://api.extremecloudiq.com
    """

    def __init__(self):
        self.host = os.environ.get("EXTREME_HOST", "api.extremecloudiq.com")
        self.api_key = os.environ.get("EXTREME_API_KEY", "")

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    # -- read operations --

    def list_vlans(self, params):
        return self._get("/vlans")

    def get_interface_status(self, params):
        device_id = params.get("device_id", "")
        if device_id:
            return self._get(f"/devices/{device_id}/interfaces")
        return self._get("/devices/interfaces")

    def list_acls(self, params):
        return self._get("/acls")

    def get_bgp_neighbors(self, params):
        device_id = params.get("device_id", "")
        return self._get(f"/devices/{device_id}/bgp/neighbors")

    def get_ospf_neighbors(self, params):
        device_id = params.get("device_id", "")
        return self._get(f"/devices/{device_id}/ospf/neighbors")

    def list_xiq_devices(self, params):
        """GET /devices — list all devices managed by ExtremeCloud IQ."""
        qp = {}
        if params.get("page"):
            qp["page"] = params["page"]
        if params.get("limit"):
            qp["limit"] = params["limit"]
        return self._get("/devices", params=qp)

    def get_switch_facts(self, params):
        device_id = params.get("device_id", "")
        return self._get(f"/devices/{device_id}")

    def get_stp_status(self, params):
        device_id = params.get("device_id", "")
        return self._get(f"/devices/{device_id}/stp")

    def list_lag_groups(self, params):
        device_id = params.get("device_id", "")
        return self._get(f"/devices/{device_id}/lag")

    def get_xiq_alerts(self, params):
        return self._get("/alerts")

    def get_port_statistics(self, params):
        device_id = params.get("device_id", "")
        return self._get(f"/devices/{device_id}/ports/statistics")


def create_extreme_server():
    server = Server("mcp-extreme")
    client = ExtremeClient()
    runner = AnsibleBridge("stevefulme1.extreme")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_vlans", description="List VLANs", inputSchema={"type": "object"}),
            Tool(name="get_interface_status", description="Get interface status", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}}),
            Tool(name="list_acls", description="List access control lists", inputSchema={"type": "object"}),
            Tool(name="get_bgp_neighbors", description="Get BGP neighbors", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="get_ospf_neighbors", description="Get OSPF neighbors", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="list_xiq_devices", description="List ExtremeCloud IQ devices", inputSchema={"type": "object", "properties": {"page": {"type": "integer"}, "limit": {"type": "integer"}}}),
            Tool(name="get_switch_facts", description="Get switch facts", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="get_stp_status", description="Get STP status", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="list_lag_groups", description="List LAG groups", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="get_xiq_alerts", description="Get ExtremeCloud IQ alerts", inputSchema={"type": "object"}),
            Tool(name="get_port_statistics", description="Get port statistics", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="create_vlan", description="Create VLAN (via Ansible)", inputSchema={"type": "object", "properties": {"vlan_id": {"type": "integer"}, "name": {"type": "string"}}, "required": ["vlan_id", "name"]}),
            Tool(name="create_acl", description="Create ACL (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "rules": {"type": "array"}}, "required": ["name"]}),
            Tool(name="configure_bgp_neighbor", description="Configure BGP neighbor (via Ansible)", inputSchema={"type": "object", "properties": {"neighbor_ip": {"type": "string"}, "remote_as": {"type": "integer"}}, "required": ["neighbor_ip", "remote_as"]}),
            Tool(name="apply_firmware", description="Apply firmware update (via Ansible)", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}, "firmware_version": {"type": "string"}}, "required": ["device_id"]}),
            Tool(name="backup_config", description="Backup switch config (via Ansible)", inputSchema={"type": "object", "properties": {"device_id": {"type": "string"}}, "required": ["device_id"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_vlans", "get_interface_status", "list_acls",
            "get_bgp_neighbors", "get_ospf_neighbors", "list_xiq_devices",
            "get_switch_facts", "get_stp_status", "list_lag_groups",
            "get_xiq_alerts", "get_port_statistics",
        }
        write_tools = {"create_vlan", "create_acl", "configure_bgp_neighbor", "apply_firmware", "backup_config"}
        if name in read_tools:
            result = await read_op(client, name, arguments)
        elif name in write_tools:
            result = await write_op(runner, name, arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    return server


def main():
    logging.basicConfig(level=logging.INFO)
    server = create_extreme_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()

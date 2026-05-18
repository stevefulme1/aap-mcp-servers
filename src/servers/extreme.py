"""MCP Server for Extreme Networks."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class ExtremeClient(BaseClient):
    """Direct API client for Extreme Networks."""

    def __init__(self):
        super().__init__("EXTREME_HOST", "EXTREME_API_KEY")


def create_extreme_server():
    """Create and configure the Extreme Networks MCP server."""
    server = create_server("mcp-extreme")
    client = ExtremeClient()
    runner = AnsibleBridge("stevefulme1.extremenetworks")

    @server.tool()
    async def list_vlans(params: dict) -> str:
        """List VLANs"""
        result = await read_op(client, "list_vlans", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_interface_status(params: dict) -> str:
        """Get interface status"""
        result = await read_op(client, "get_interface_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_acls(params: dict) -> str:
        """List access control lists"""
        result = await read_op(client, "list_acls", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_bgp_neighbors(params: dict) -> str:
        """Get BGP neighbors"""
        result = await read_op(client, "get_bgp_neighbors", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_ospf_neighbors(params: dict) -> str:
        """Get OSPF neighbors"""
        result = await read_op(client, "get_ospf_neighbors", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_xiq_devices(params: dict) -> str:
        """List ExtremeCloud IQ devices"""
        result = await read_op(client, "list_xiq_devices", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_switch_facts(params: dict) -> str:
        """Get switch facts"""
        result = await read_op(client, "get_switch_facts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_stp_status(params: dict) -> str:
        """Get STP status"""
        result = await read_op(client, "get_stp_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_lag_groups(params: dict) -> str:
        """List LAG groups"""
        result = await read_op(client, "list_lag_groups", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_xiq_alerts(params: dict) -> str:
        """Get ExtremeCloud IQ alerts"""
        result = await read_op(client, "get_xiq_alerts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_port_statistics(params: dict) -> str:
        """Get port statistics"""
        result = await read_op(client, "get_port_statistics", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_vlan(params: dict) -> str:
        """Create VLAN"""
        result = await write_op(runner, "create_vlan", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_acl(params: dict) -> str:
        """Create ACL"""
        result = await write_op(runner, "create_acl", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def configure_bgp_neighbor(params: dict) -> str:
        """Configure BGP neighbor"""
        result = await write_op(runner, "configure_bgp_neighbor", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def apply_firmware(params: dict) -> str:
        """Apply firmware update"""
        result = await write_op(runner, "apply_firmware", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def backup_config(params: dict) -> str:
        """Backup switch config"""
        result = await write_op(runner, "backup_config", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the Extreme Networks MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_extreme_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()

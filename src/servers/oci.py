"""MCP Server for Oracle Cloud Infrastructure."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class OciClient(BaseClient):
    """Direct API client for Oracle Cloud Infrastructure."""

    def __init__(self):
        super().__init__("OCI_HOST", "OCI_API_KEY")


def create_oci_server():
    """Create and configure the Oracle Cloud Infrastructure MCP server."""
    server = create_server("mcp-oci")
    client = OciClient()
    runner = AnsibleBridge("stevefulme1.oci_cloud")

    @server.tool()
    async def list_instances(params: dict) -> str:
        """List compute instances"""
        result = await read_op(client, "list_instances", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_vcns(params: dict) -> str:
        """List VCNs"""
        result = await read_op(client, "list_vcns", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_subnets(params: dict) -> str:
        """List subnets"""
        result = await read_op(client, "list_subnets", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_databases(params: dict) -> str:
        """List databases"""
        result = await read_op(client, "list_databases", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_buckets(params: dict) -> str:
        """List Object Storage buckets"""
        result = await read_op(client, "list_buckets", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_load_balancers(params: dict) -> str:
        """List load balancers"""
        result = await read_op(client, "list_load_balancers", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_compartment_usage(params: dict) -> str:
        """Get compartment usage"""
        result = await read_op(client, "get_compartment_usage", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_security_lists(params: dict) -> str:
        """List security lists"""
        result = await read_op(client, "list_security_lists", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_block_volumes(params: dict) -> str:
        """List block volumes"""
        result = await read_op(client, "list_block_volumes", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_availability_domains(params: dict) -> str:
        """Get availability domains"""
        result = await read_op(client, "get_availability_domains", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_limits(params: dict) -> str:
        """Get service limits"""
        result = await read_op(client, "get_limits", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_instance(params: dict) -> str:
        """Create compute instance"""
        result = await write_op(runner, "create_instance", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_vcn(params: dict) -> str:
        """Create VCN"""
        result = await write_op(runner, "create_vcn", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_bucket(params: dict) -> str:
        """Create Object Storage bucket"""
        result = await write_op(runner, "create_bucket", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_database(params: dict) -> str:
        """Create database"""
        result = await write_op(runner, "create_database", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def manage_security_list(params: dict) -> str:
        """Manage security list rules"""
        result = await write_op(runner, "manage_security_list", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the Oracle Cloud Infrastructure MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_oci_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()

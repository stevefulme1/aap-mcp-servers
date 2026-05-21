"""MCP Server for Oracle Cloud Infrastructure (OCI)."""

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
    import oci as oci_sdk
    HAS_OCI = True
except ImportError:
    HAS_OCI = False


async def read_op(client, operation, params):
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class OCIClient(BaseClient):
    """Direct client for Oracle Cloud Infrastructure.

    Uses OCI Python SDK for API-key or instance-principal signing.
    Base: https://iaas.{region}.oraclecloud.com
    """

    def __init__(self):
        self.host = os.environ.get("OCI_HOST", "")
        self.api_key = ""  # not used directly
        self.region = os.environ.get("OCI_REGION", "us-ashburn-1")
        self.compartment = os.environ.get("OCI_COMPARTMENT_ID", "")
        self._config = None
        self._compute = None
        self._network = None
        self._db = None
        self._os_client = None
        self._lb = None
        self._identity = None
        self._limits = None

    def _oci_config(self):
        if self._config is None:
            if not HAS_OCI:
                raise RuntimeError("oci SDK not installed")
            config_file = os.environ.get("OCI_CONFIG_FILE", "~/.oci/config")
            profile = os.environ.get("OCI_PROFILE", "DEFAULT")
            self._config = oci_sdk.config.from_file(config_file, profile)
        return self._config

    def _get_compute(self):
        if self._compute is None:
            self._compute = oci_sdk.core.ComputeClient(self._oci_config())
        return self._compute

    def _get_network(self):
        if self._network is None:
            self._network = oci_sdk.core.VirtualNetworkClient(self._oci_config())
        return self._network

    def _get_db(self):
        if self._db is None:
            self._db = oci_sdk.database.DatabaseClient(self._oci_config())
        return self._db

    def _get_object_storage(self):
        if self._os_client is None:
            self._os_client = oci_sdk.object_storage.ObjectStorageClient(self._oci_config())
        return self._os_client

    def _get_lb(self):
        if self._lb is None:
            self._lb = oci_sdk.load_balancer.LoadBalancerClient(self._oci_config())
        return self._lb

    def _get_identity(self):
        if self._identity is None:
            self._identity = oci_sdk.identity.IdentityClient(self._oci_config())
        return self._identity

    def _get_limits(self):
        if self._limits is None:
            self._limits = oci_sdk.limits.LimitsClient(self._oci_config())
        return self._limits

    def _cid(self, params):
        return params.get("compartment_id", self.compartment)

    def _ser(self, obj):
        """Serialize OCI data objects."""
        if hasattr(obj, 'data'):
            obj = obj.data
        if isinstance(obj, list):
            return [self._ser(i) for i in obj]
        if hasattr(obj, '__dict__'):
            return {k: str(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj

    # -- read operations --

    def list_instances(self, params):
        resp = self._get_compute().list_instances(self._cid(params))
        return {"instances": self._ser(resp.data)}

    def list_vcns(self, params):
        resp = self._get_network().list_vcns(self._cid(params))
        return {"vcns": self._ser(resp.data)}

    def list_subnets(self, params):
        resp = self._get_network().list_subnets(self._cid(params))
        return {"subnets": self._ser(resp.data)}

    def list_databases(self, params):
        resp = self._get_db().list_db_systems(self._cid(params))
        return {"db_systems": self._ser(resp.data)}

    def list_buckets(self, params):
        namespace = self._get_object_storage().get_namespace().data
        resp = self._get_object_storage().list_buckets(namespace, self._cid(params))
        return {"buckets": self._ser(resp.data)}

    def list_load_balancers(self, params):
        resp = self._get_lb().list_load_balancers(self._cid(params))
        return {"load_balancers": self._ser(resp.data)}

    def get_compartment_usage(self, params):
        cid = self._cid(params)
        identity = self._get_identity()
        resp = identity.get_compartment(cid)
        return self._ser(resp.data)

    def list_security_lists(self, params):
        resp = self._get_network().list_security_lists(self._cid(params))
        return {"security_lists": self._ser(resp.data)}

    def list_block_volumes(self, params):
        client = oci_sdk.core.BlockstorageClient(self._oci_config())
        resp = client.list_volumes(self._cid(params))
        return {"volumes": self._ser(resp.data)}

    def get_availability_domains(self, params):
        resp = self._get_identity().list_availability_domains(self._cid(params))
        return {"availability_domains": self._ser(resp.data)}

    def get_limits(self, params):
        service = params.get("service_name", "compute")
        resp = self._get_limits().list_limit_values(self._cid(params), service_name=service)
        return {"limits": self._ser(resp.data)}


def create_oci_server():
    server = Server("mcp-oci")
    client = OCIClient()
    runner = AnsibleBridge("stevefulme1.oci")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_instances", description="List compute instances", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_vcns", description="List VCNs", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_subnets", description="List subnets", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_databases", description="List databases", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_buckets", description="List Object Storage buckets", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_load_balancers", description="List load balancers", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="get_compartment_usage", description="Get compartment usage", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_security_lists", description="List security lists", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="list_block_volumes", description="List block volumes", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="get_availability_domains", description="Get availability domains", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}}}),
            Tool(name="get_limits", description="Get service limits", inputSchema={"type": "object", "properties": {"compartment_id": {"type": "string"}, "service_name": {"type": "string"}}}),
            Tool(name="create_instance", description="Create compute instance (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "shape": {"type": "string"}, "compartment_id": {"type": "string"}}, "required": ["name", "shape"]}),
            Tool(name="create_vcn", description="Create VCN (via Ansible)", inputSchema={"type": "object", "properties": {"display_name": {"type": "string"}, "cidr_block": {"type": "string"}}, "required": ["display_name", "cidr_block"]}),
            Tool(name="create_bucket", description="Create Object Storage bucket (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "compartment_id": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_database", description="Create database (via Ansible)", inputSchema={"type": "object", "properties": {"db_name": {"type": "string"}}, "required": ["db_name"]}),
            Tool(name="manage_security_list", description="Manage security list rules (via Ansible)", inputSchema={"type": "object", "properties": {"security_list_id": {"type": "string"}, "rules": {"type": "array"}}, "required": ["security_list_id"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_instances", "list_vcns", "list_subnets", "list_databases",
            "list_buckets", "list_load_balancers", "get_compartment_usage",
            "list_security_lists", "list_block_volumes",
            "get_availability_domains", "get_limits",
        }
        write_tools = {"create_instance", "create_vcn", "create_bucket", "create_database", "manage_security_list"}
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
    server = create_oci_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()

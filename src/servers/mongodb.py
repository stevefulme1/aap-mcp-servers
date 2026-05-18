"""MCP Server for MongoDB."""

import asyncio
import json
import logging

from src.common.client import BaseClient
from src.common.bridge import AnsibleBridge
from src.common.factory import create_server, read_op, write_op, run_server

logger = logging.getLogger(__name__)


class MongodbClient(BaseClient):
    """Direct API client for MongoDB."""

    def __init__(self):
        super().__init__("MONGODB_HOST", "MONGODB_API_KEY")


def create_mongodb_server():
    """Create and configure the MongoDB MCP server."""
    server = create_server("mcp-mongodb")
    client = MongodbClient()
    runner = AnsibleBridge("stevefulme1.mongodb")

    @server.tool()
    async def query_collection(params: dict) -> str:
        """Query a MongoDB collection"""
        result = await read_op(client, "query_collection", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_databases(params: dict) -> str:
        """List all databases"""
        result = await read_op(client, "list_databases", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def list_collections(params: dict) -> str:
        """List collections in a database"""
        result = await read_op(client, "list_collections", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_indexes(params: dict) -> str:
        """Get indexes for a collection"""
        result = await read_op(client, "get_indexes", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_replication_status(params: dict) -> str:
        """Get replica set status"""
        result = await read_op(client, "get_replication_status", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_cluster_stats(params: dict) -> str:
        """Get cluster statistics"""
        result = await read_op(client, "get_cluster_stats", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_user_list(params: dict) -> str:
        """List database users"""
        result = await read_op(client, "get_user_list", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def aggregate(params: dict) -> str:
        """Run aggregation pipeline"""
        result = await read_op(client, "aggregate", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def explain_query(params: dict) -> str:
        """Explain query execution plan"""
        result = await read_op(client, "explain_query", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_atlas_clusters(params: dict) -> str:
        """List Atlas clusters"""
        result = await read_op(client, "get_atlas_clusters", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_atlas_alerts(params: dict) -> str:
        """Get Atlas alerts"""
        result = await read_op(client, "get_atlas_alerts", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def get_atlas_backup_snapshots(params: dict) -> str:
        """List Atlas backup snapshots"""
        result = await read_op(client, "get_atlas_backup_snapshots", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_index(params: dict) -> str:
        """Create an index"""
        result = await write_op(runner, "create_index", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def create_user(params: dict) -> str:
        """Create a database user"""
        result = await write_op(runner, "create_user", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def drop_collection(params: dict) -> str:
        """Drop a collection"""
        result = await write_op(runner, "drop_collection", params)
        return json.dumps(result, indent=2, default=str)

    @server.tool()
    async def configure_atlas_backup(params: dict) -> str:
        """Configure Atlas backup schedule"""
        result = await write_op(runner, "configure_atlas_backup", params)
        return json.dumps(result, indent=2, default=str)

    return server


def main():
    """Run the MongoDB MCP server."""
    logging.basicConfig(level=logging.INFO)
    server = create_mongodb_server()
    asyncio.run(run_server(server))


if __name__ == "__main__":
    main()

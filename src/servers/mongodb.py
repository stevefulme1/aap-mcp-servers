"""MCP Server for MongoDB (pymongo driver + Atlas REST API)."""

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

try:
    from pymongo import MongoClient as PyMongoClient
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False

try:
    from requests.auth import HTTPDigestAuth
    HAS_DIGEST = True
except ImportError:
    HAS_DIGEST = False


async def read_op(client, operation, params):
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class MongoDBClient(BaseClient):
    """Direct client for MongoDB.

    Local ops use pymongo.  Atlas management uses the Atlas Admin API v2
    with digest auth at https://cloud.mongodb.com/api/atlas/v2.
    """

    def __init__(self):
        self.host = os.environ.get("MONGODB_HOST", "localhost")
        self.port = int(os.environ.get("MONGODB_PORT", "27017"))
        self.uri = os.environ.get("MONGODB_URI", "")
        self.api_key = os.environ.get("MONGODB_API_KEY", "")
        # Atlas API credentials (public + private key for digest auth)
        self.atlas_public = os.environ.get("ATLAS_PUBLIC_KEY", "")
        self.atlas_private = os.environ.get("ATLAS_PRIVATE_KEY", "")
        self.atlas_group = os.environ.get("ATLAS_GROUP_ID", "")

    def _mongo(self):
        """Return a pymongo client."""
        if not HAS_PYMONGO:
            raise RuntimeError("pymongo not installed")
        if self.uri:
            return PyMongoClient(self.uri)
        return PyMongoClient(self.host, self.port)

    def _atlas_get(self, path, params=None):
        """GET against the Atlas Admin API v2 (digest auth)."""
        url = f"https://cloud.mongodb.com/api/atlas/v2{path}"
        auth = HTTPDigestAuth(self.atlas_public, self.atlas_private)
        headers = {"Content-Type": "application/json", "Accept": "application/vnd.atlas.2023-02-01+json"}
        resp = requests.get(url, auth=auth, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # -- pymongo read operations --

    def query_collection(self, params):
        db_name = params.get("database", "test")
        coll = params.get("collection", "test")
        query_filter = params.get("filter", {})
        limit = params.get("limit", 20)
        client = self._mongo()
        try:
            docs = list(client[db_name][coll].find(query_filter).limit(limit))
            for d in docs:
                if "_id" in d:
                    d["_id"] = str(d["_id"])
            return {"results": docs, "count": len(docs)}
        finally:
            client.close()

    def list_databases(self, params):
        client = self._mongo()
        try:
            return {"databases": client.list_database_names()}
        finally:
            client.close()

    def list_collections(self, params):
        db_name = params.get("database", "test")
        client = self._mongo()
        try:
            return {"collections": client[db_name].list_collection_names()}
        finally:
            client.close()

    def get_indexes(self, params):
        db_name = params.get("database", "test")
        coll = params.get("collection", "test")
        client = self._mongo()
        try:
            idxs = list(client[db_name][coll].list_indexes())
            return {"indexes": idxs}
        finally:
            client.close()

    def get_replication_status(self, params):
        client = self._mongo()
        try:
            return client.admin.command("replSetGetStatus")
        finally:
            client.close()

    def get_cluster_stats(self, params):
        db_name = params.get("database", "test")
        client = self._mongo()
        try:
            return client[db_name].command("dbStats")
        finally:
            client.close()

    def get_user_list(self, params):
        db_name = params.get("database", "admin")
        client = self._mongo()
        try:
            return client[db_name].command("usersInfo")
        finally:
            client.close()

    def aggregate(self, params):
        db_name = params.get("database", "test")
        coll = params.get("collection", "test")
        pipeline = params.get("pipeline", [])
        client = self._mongo()
        try:
            docs = list(client[db_name][coll].aggregate(pipeline))
            for d in docs:
                if "_id" in d:
                    d["_id"] = str(d["_id"])
            return {"results": docs}
        finally:
            client.close()

    def explain_query(self, params):
        db_name = params.get("database", "test")
        coll = params.get("collection", "test")
        query_filter = params.get("filter", {})
        client = self._mongo()
        try:
            return client[db_name][coll].find(query_filter).explain()
        finally:
            client.close()

    # -- Atlas API read operations --

    def get_atlas_clusters(self, params):
        group = params.get("group_id", self.atlas_group)
        return self._atlas_get(f"/groups/{group}/clusters")

    def get_atlas_alerts(self, params):
        group = params.get("group_id", self.atlas_group)
        return self._atlas_get(f"/groups/{group}/alerts")

    def get_atlas_backup_snapshots(self, params):
        group = params.get("group_id", self.atlas_group)
        cluster = params.get("cluster_name", "")
        return self._atlas_get(f"/groups/{group}/clusters/{cluster}/backup/snapshots")


def create_mongodb_server():
    server = Server("mcp-mongodb")
    client = MongoDBClient()
    runner = AnsibleBridge("stevefulme1.mongodb")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(
                name="query_collection",
                description="Query a MongoDB collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "description": "Database name"},
                        "collection": {"type": "string", "description": "Collection name"},
                        "filter": {"type": "object", "description": "MongoDB query filter"},
                        "limit": {"type": "integer", "description": "Max documents to return"},
                    },
                    "required": ["database", "collection"],
                },
            ),
            Tool(name="list_databases", description="List all databases", inputSchema={"type": "object"}),
            Tool(
                name="list_collections",
                description="List collections in a database",
                inputSchema={
                    "type": "object",
                    "properties": {"database": {"type": "string"}},
                    "required": ["database"],
                },
            ),
            Tool(
                name="get_indexes",
                description="Get indexes for a collection",
                inputSchema={
                    "type": "object",
                    "properties": {"database": {"type": "string"}, "collection": {"type": "string"}},
                    "required": ["database", "collection"],
                },
            ),
            Tool(name="get_replication_status", description="Get replica set status", inputSchema={"type": "object"}),
            Tool(
                name="get_cluster_stats",
                description="Get cluster statistics",
                inputSchema={
                    "type": "object",
                    "properties": {"database": {"type": "string"}},
                },
            ),
            Tool(name="get_user_list", description="List database users", inputSchema={"type": "object", "properties": {"database": {"type": "string"}}}),
            Tool(
                name="aggregate",
                description="Run aggregation pipeline",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "collection": {"type": "string"},
                        "pipeline": {"type": "array", "description": "Aggregation pipeline stages"},
                    },
                    "required": ["database", "collection", "pipeline"],
                },
            ),
            Tool(
                name="explain_query",
                description="Explain query execution plan",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "collection": {"type": "string"},
                        "filter": {"type": "object"},
                    },
                    "required": ["database", "collection"],
                },
            ),
            Tool(name="get_atlas_clusters", description="List Atlas clusters", inputSchema={"type": "object", "properties": {"group_id": {"type": "string"}}}),
            Tool(name="get_atlas_alerts", description="Get Atlas alerts", inputSchema={"type": "object", "properties": {"group_id": {"type": "string"}}}),
            Tool(
                name="get_atlas_backup_snapshots",
                description="List Atlas backup snapshots",
                inputSchema={
                    "type": "object",
                    "properties": {"group_id": {"type": "string"}, "cluster_name": {"type": "string"}},
                    "required": ["cluster_name"],
                },
            ),
            Tool(name="create_index", description="Create an index (via Ansible)", inputSchema={"type": "object", "properties": {"database": {"type": "string"}, "collection": {"type": "string"}, "keys": {"type": "object"}}, "required": ["database", "collection", "keys"]}),
            Tool(name="create_user", description="Create a database user (via Ansible)", inputSchema={"type": "object", "properties": {"database": {"type": "string"}, "name": {"type": "string"}, "password": {"type": "string"}}, "required": ["database", "name"]}),
            Tool(name="drop_collection", description="Drop a collection (via Ansible)", inputSchema={"type": "object", "properties": {"database": {"type": "string"}, "collection": {"type": "string"}}, "required": ["database", "collection"]}),
            Tool(name="configure_atlas_backup", description="Configure Atlas backup schedule (via Ansible)", inputSchema={"type": "object", "properties": {"cluster_name": {"type": "string"}}, "required": ["cluster_name"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "query_collection", "list_databases", "list_collections",
            "get_indexes", "get_replication_status", "get_cluster_stats",
            "get_user_list", "aggregate", "explain_query",
            "get_atlas_clusters", "get_atlas_alerts", "get_atlas_backup_snapshots",
        }
        write_tools = {"create_index", "create_user", "drop_collection", "configure_atlas_backup"}
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
    server = create_mongodb_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()

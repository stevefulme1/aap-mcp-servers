"""Server factory for creating MCP servers."""

import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

logger = logging.getLogger(__name__)


def create_server(name):
    """Create a new MCP server instance."""
    return Server(name)


async def run_server(server):
    """Run an MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

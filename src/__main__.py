"""CLI entry point for running any MCP server."""

import sys

SERVERS = [
    "elastic",
    "weka",
    "mongodb",
    "datadog",
    "coreweave",
    "ddn",
    "newrelic",
    "oci",
    "truenas",
    "vastdata",
    "oracledb",
    "mssql",
    "extreme"
]


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SERVERS:
        print("Usage: python -m src <server>")
        print(f"Available servers: {', '.join(SERVERS)}")
        sys.exit(1)

    name = sys.argv[1]
    module = __import__(f"src.servers.{name}", fromlist=["main"])
    module.main()


if __name__ == "__main__":
    main()

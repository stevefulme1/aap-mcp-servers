# AAP MCP Servers

Unified MCP server monorepo for Ansible Automation Platform — 13 vendor integrations with hybrid read/write architecture.

## Architecture

```
AI Agent (Claude, etc.)
    |
    v
+-----------------------------+
|  MCP Server (per vendor)    |
|  +---------+  +-----------+ |
|  |BaseClient|  |AnsibleBridge| |
|  | (reads) |  | (writes)  | |
|  +----+----+  +-----+-----+ |
+-------+-------------+-------+
        |              |
        v              v
   Vendor API     AAP Controller
   (direct)       (governed)
```

Reads go directly to vendor APIs. Writes route through ansible-runner to AAP Controller for RBAC, approvals, and audit.

## Servers

| Server | Vendor | Read | Write | Collection |
|--------|--------|------|-------|------------|
| mcp-elastic | Elastic Stack | 11 | 5 | stevefulme1.elastic |
| mcp-weka | WekaIO | 11 | 5 | stevefulme1.weka |
| mcp-mongodb | MongoDB | 12 | 4 | stevefulme1.mongodb |
| mcp-datadog | Datadog | 10 | 6 | stevefulme1.datadog |
| mcp-coreweave | CoreWeave | 11 | 5 | stevefulme1.coreweave |
| mcp-ddn | DDN Storage | 11 | 5 | stevefulme1.ddn |
| mcp-newrelic | New Relic | 10 | 6 | stevefulme1.newrelic |
| mcp-oci | Oracle Cloud | 11 | 5 | stevefulme1.oci_cloud |
| mcp-truenas | TrueNAS | 11 | 5 | stevefulme1.truenas |
| mcp-vastdata | VAST Data | 11 | 5 | stevefulme1.vastdata |
| mcp-oracledb | Oracle DB | 11 | 5 | stevefulme1.oracledb |
| mcp-mssql | SQL Server | 11 | 5 | stevefulme1.mssql |
| mcp-extreme | Extreme Networks | 11 | 5 | stevefulme1.extremenetworks |

**Total: 143 read + 68 write = 211 tools**

## Quick Start

```bash
pip install -e .
ELASTIC_HOST=es.example.com ELASTIC_API_KEY=xxx mcp-elastic
```

## Docker

```bash
docker build -t aap-mcp .
docker run -e ELASTIC_HOST=es.example.com aap-mcp elastic
```

## Claude Code Integration

```json
{
  "mcpServers": {
    "elastic": {
      "command": "mcp-elastic",
      "env": {
        "ELASTIC_HOST": "es.example.com",
        "ELASTIC_API_KEY": "your-key"
      }
    }
  }
}
```

## License

GPL-3.0-or-later

# Changelog

## [Unreleased]

### Maintenance
- Expanded .gitignore with standard patterns for secrets, IDE files, and OS metadata

## [1.0.0] - 2026-05-18

### Added
- Unified monorepo consolidating 13 individual MCP server repositories
- Shared base classes: BaseClient (reads), AnsibleBridge (writes)
- CLI: `python -m src <server>` or `mcp-<vendor>` entry points
- Docker support
- 13 vendor servers: elastic, weka, mongodb, datadog, coreweave, ddn, newrelic, oci, truenas, vastdata, oracledb, mssql, extreme
- 211 total tools (143 read + 68 write) across all servers
- Unit tests for all servers and shared components

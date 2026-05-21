"""MCP Server for CoreWeave GPU Cloud (Kubernetes API)."""

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
    from kubernetes import client as k8s_client, config as k8s_config
    HAS_K8S = True
except ImportError:
    HAS_K8S = False


async def read_op(client, operation, params):
    return await client.query(operation, params)


async def write_op(runner, operation, params):
    return await runner.execute(operation, params)


class CoreWeaveClient(BaseClient):
    """Direct client for CoreWeave via Kubernetes API.

    CoreWeave exposes a standard Kubernetes API.  Uses kubeconfig or
    in-cluster config for authentication.
    """

    def __init__(self):
        self.host = os.environ.get("COREWEAVE_HOST", "")
        self.api_key = ""  # uses kubeconfig
        self.kubeconfig = os.environ.get("KUBECONFIG", "")
        self.namespace = os.environ.get("COREWEAVE_NAMESPACE", "default")
        self._core = None
        self._apps = None
        self._batch = None
        self._custom = None

    def _load_config(self):
        if not HAS_K8S:
            raise RuntimeError("kubernetes client not installed")
        if self.kubeconfig:
            k8s_config.load_kube_config(config_file=self.kubeconfig)
        else:
            try:
                k8s_config.load_incluster_config()
            except k8s_config.ConfigException:
                k8s_config.load_kube_config()

    def _get_core(self):
        if self._core is None:
            self._load_config()
            self._core = k8s_client.CoreV1Api()
        return self._core

    def _get_apps(self):
        if self._apps is None:
            self._load_config()
            self._apps = k8s_client.AppsV1Api()
        return self._apps

    def _get_batch(self):
        if self._batch is None:
            self._load_config()
            self._batch = k8s_client.BatchV1Api()
        return self._batch

    def _get_custom(self):
        if self._custom is None:
            self._load_config()
            self._custom = k8s_client.CustomObjectsApi()
        return self._custom

    def _ser(self, obj):
        """Serialize K8s API objects to JSON-safe dicts."""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if isinstance(obj, list):
            return [self._ser(i) for i in obj]
        return obj

    def _ns(self, params):
        return params.get("namespace", self.namespace)

    # -- read operations --

    def list_virtual_servers(self, params):
        """List VirtualServer CRDs (CoreWeave custom resource)."""
        try:
            items = self._get_custom().list_namespaced_custom_object(
                group="virtualservers.coreweave.com", version="v1alpha1",
                namespace=self._ns(params), plural="virtualservers",
            )
            return items
        except Exception:
            # Fallback to listing pods with vs label
            pods = self._get_core().list_namespaced_pod(self._ns(params))
            return {"pods": [{"name": p.metadata.name, "status": p.status.phase} for p in pods.items]}

    def get_gpu_availability(self, params):
        """Check GPU node capacity."""
        nodes = self._get_core().list_node()
        gpu_nodes = []
        for n in nodes.items:
            gpu_count = n.status.allocatable.get("nvidia.com/gpu", "0") if n.status.allocatable else "0"
            if int(gpu_count) > 0:
                gpu_nodes.append({
                    "name": n.metadata.name,
                    "gpu_count": gpu_count,
                    "gpu_type": n.metadata.labels.get("gpu.nvidia.com/class", "unknown"),
                })
        return {"gpu_nodes": gpu_nodes}

    def list_inference_services(self, params):
        """List InferenceService CRDs (KServe)."""
        try:
            return self._get_custom().list_namespaced_custom_object(
                group="serving.kserve.io", version="v1beta1",
                namespace=self._ns(params), plural="inferenceservices",
            )
        except Exception:
            return {"items": []}

    def list_vpcs(self, params):
        """List NetworkAttachmentDefinitions (VPC equivalent)."""
        try:
            return self._get_custom().list_namespaced_custom_object(
                group="k8s.cni.cncf.io", version="v1",
                namespace=self._ns(params), plural="network-attachment-definitions",
            )
        except Exception:
            return {"items": []}

    def list_storage_volumes(self, params):
        pvcs = self._get_core().list_namespaced_persistent_volume_claim(self._ns(params))
        return {"pvcs": [{"name": p.metadata.name, "capacity": str(p.spec.resources.requests.get("storage", "")) if p.spec.resources and p.spec.resources.requests else "", "status": p.status.phase} for p in pvcs.items]}

    def list_node_pools(self, params):
        nodes = self._get_core().list_node()
        pools = {}
        for n in nodes.items:
            pool = n.metadata.labels.get("node.coreweave.cloud/class", "default")
            pools.setdefault(pool, []).append(n.metadata.name)
        return {"node_pools": {k: {"count": len(v), "nodes": v} for k, v in pools.items()}}

    def get_workload_metrics(self, params):
        """Get pod resource usage from metrics API."""
        ns = self._ns(params)
        pods = self._get_core().list_namespaced_pod(ns)
        return {"pod_count": len(pods.items), "pods": [{"name": p.metadata.name, "status": p.status.phase} for p in pods.items[:20]]}

    def list_namespaces(self, params):
        ns_list = self._get_core().list_namespace()
        return {"namespaces": [n.metadata.name for n in ns_list.items]}

    def list_jobs(self, params):
        jobs = self._get_batch().list_namespaced_job(self._ns(params))
        return {"jobs": [{"name": j.metadata.name, "active": j.status.active, "succeeded": j.status.succeeded, "failed": j.status.failed} for j in jobs.items]}

    def get_billing_summary(self, params):
        """Approximate billing from node + GPU allocations."""
        nodes = self._get_core().list_node()
        total_gpu = sum(int(n.status.allocatable.get("nvidia.com/gpu", "0") if n.status.allocatable else "0") for n in nodes.items)
        return {"total_nodes": len(nodes.items), "total_gpus": total_gpu}

    def get_gpu_inventory(self, params):
        nodes = self._get_core().list_node()
        inventory = {}
        for n in nodes.items:
            gpu_type = n.metadata.labels.get("gpu.nvidia.com/class", "none")
            gpu_count = int(n.status.allocatable.get("nvidia.com/gpu", "0") if n.status.allocatable else "0")
            if gpu_count > 0:
                inventory.setdefault(gpu_type, 0)
                inventory[gpu_type] += gpu_count
        return {"gpu_inventory": inventory}


def create_coreweave_server():
    server = Server("mcp-coreweave")
    client = CoreWeaveClient()
    runner = AnsibleBridge("stevefulme1.coreweave")

    @server.list_tools()
    async def handle_list_tools():
        return [
            Tool(name="list_virtual_servers", description="List virtual servers", inputSchema={"type": "object", "properties": {"namespace": {"type": "string"}}}),
            Tool(name="get_gpu_availability", description="Check GPU availability by type", inputSchema={"type": "object"}),
            Tool(name="list_inference_services", description="List inference services", inputSchema={"type": "object", "properties": {"namespace": {"type": "string"}}}),
            Tool(name="list_vpcs", description="List VPCs", inputSchema={"type": "object", "properties": {"namespace": {"type": "string"}}}),
            Tool(name="list_storage_volumes", description="List storage volumes", inputSchema={"type": "object", "properties": {"namespace": {"type": "string"}}}),
            Tool(name="list_node_pools", description="List node pools", inputSchema={"type": "object"}),
            Tool(name="get_workload_metrics", description="Get workload metrics", inputSchema={"type": "object", "properties": {"namespace": {"type": "string"}}}),
            Tool(name="list_namespaces", description="List namespaces", inputSchema={"type": "object"}),
            Tool(name="list_jobs", description="List running jobs", inputSchema={"type": "object", "properties": {"namespace": {"type": "string"}}}),
            Tool(name="get_billing_summary", description="Get billing summary", inputSchema={"type": "object"}),
            Tool(name="get_gpu_inventory", description="Get full GPU inventory", inputSchema={"type": "object"}),
            Tool(name="create_virtual_server", description="Create a virtual server (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "gpu_type": {"type": "string"}, "gpu_count": {"type": "integer"}}, "required": ["name"]}),
            Tool(name="deploy_inference_service", description="Deploy an inference service (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "model": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_vpc", description="Create a VPC (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "cidr": {"type": "string"}}, "required": ["name"]}),
            Tool(name="create_storage_volume", description="Create storage volume (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "size": {"type": "string"}}, "required": ["name", "size"]}),
            Tool(name="scale_workload", description="Scale a workload (via Ansible)", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "replicas": {"type": "integer"}}, "required": ["name", "replicas"]}),
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict):
        read_tools = {
            "list_virtual_servers", "get_gpu_availability",
            "list_inference_services", "list_vpcs", "list_storage_volumes",
            "list_node_pools", "get_workload_metrics", "list_namespaces",
            "list_jobs", "get_billing_summary", "get_gpu_inventory",
        }
        write_tools = {"create_virtual_server", "deploy_inference_service", "create_vpc", "create_storage_volume", "scale_workload"}
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
    server = create_coreweave_server()
    asyncio.run(_run(server))


async def _run(server):
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    main()

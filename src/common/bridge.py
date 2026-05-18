"""Ansible runner bridge for write operations."""

import logging
import os

logger = logging.getLogger(__name__)


class AnsibleBridge:
    """Route write operations through ansible-runner to AAP Controller."""

    def __init__(self, collection):
        self.collection = collection
        self.controller_url = os.environ.get("AAP_CONTROLLER_URL", "")
        self.controller_token = os.environ.get("AAP_CONTROLLER_TOKEN", "")

    async def execute(self, module_name, params):
        """Execute an Ansible module via ansible-runner."""
        try:
            import ansible_runner
        except ImportError:
            return {
                "status": "failed",
                "msg": "ansible-runner not installed",
            }

        result = ansible_runner.run(
            module=f"{self.collection}.{module_name}",
            module_args=params,
            quiet=True,
        )
        return {
            "status": result.status,
            "rc": result.rc,
            "stdout": result.stdout.read() if result.stdout else "",
        }

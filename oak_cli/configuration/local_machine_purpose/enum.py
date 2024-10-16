from oak_cli.utils.types import CustomEnum


class LocalMachinePurpose(CustomEnum):
    """A machine can have one, multiple, or all of these purposes."""

    INITIAL = "initial"

    EVERYTHING = "everything"

    ROOT_ORCHESTRATOR = "root_orchestrator"
    CLUSTER_ORCHESTRATOR = "cluster_orchestrator"
    WORKER_NODE = "worker_node"

    ADDON_SUPPORT = "addon_support"

    DEVELOPMENT = "development"

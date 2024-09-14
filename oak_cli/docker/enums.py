from enum import EnumMeta

from oak_cli.utils.types import CustomEnum


class OakestraDockerComposeService(CustomEnum, metaclass=EnumMeta):
    pass


class RootOrchestratorService(OakestraDockerComposeService):
    SYSTEM_MANAGER = "system_manager"
    MONGO_ROOT = "mongo_root"
    MONGO_ROOTNET = "mongo_rootnet"
    ROOT_SERVICE_MANAGER = "root_service_manager"
    REDIS = "redis"
    GRAFANA = "grafana"
    DASHBOARD = "dashboard"
    CLOUD_SCHEDULER = "cloud_scheduler"
    RESOURCE_ABSTRACTOR = "resource_abstractor"


class ClusterOrchestratorService(OakestraDockerComposeService):
    MQTT = "mqtt"
    MONGO_CLUSTER = "mongo_cluster"
    MONGO_CLUSTERNET = "mongo_clusternet"
    CLUSTER_SERVICE_MANAGER = "cluster_service_manager"
    CLUSTER_MANAGER = "cluster_manager"
    CLUSTER_SCHEDULER = "cluster_scheduler"
    CLUSTER_REDIS = "cluster_redis"
    PROMETHEUS = "prometheus"

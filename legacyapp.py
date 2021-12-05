import pulumi
import pulumi_kubernetes as k8s
from ekscluster import cluster

legacy_app = k8s.yaml.ConfigGroup(
    "legacy",
    files=["./kube-manifest/app.yaml"],
    opts = pulumi.ResourceOptions(
        provider = cluster.provider
    )
)
import pulumi
import pulumi_eks as eks

# Create an EKS cluster with the default configuration.
cluster = eks.Cluster('my-cluster')

pulumi.export('cluster-name', cluster.name)
# Export the cluster's kubeconfig.
pulumi.export('kubeconfig', cluster.kubeconfig)
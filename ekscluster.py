import pulumi_eks as eks

# Create an EKS cluster with the default configuration.
cluster = eks.Cluster('my-cluster')

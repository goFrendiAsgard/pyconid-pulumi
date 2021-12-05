import pulumi
from ekscluster import cluster
from app import deployment, service
from legacyapp import legacy_app
from kubedashboard import kube_dashboard

# Export the URL for the load balanced service.
pulumi.export('url', service.status.load_balancer.ingress[0].hostname)

# Export the cluster's kubeconfig.
pulumi.export('kubeconfig', cluster.kubeconfig)
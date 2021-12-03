import pulumi
import pulumi_eks as eks
import pulumi_kubernetes as k8s

# Create an EKS cluster with the default configuration.
cluster = eks.Cluster('my-cluster')

# Deploy a small canary service (NGINX), to test that the cluster is working.
app_name = 'my-app'
app_labels = { 'app': app_name }
deployment = k8s.apps.v1.Deployment(f'{app_name}-dep',
    spec = k8s.apps.v1.DeploymentSpecArgs(
        selector = k8s.meta.v1.LabelSelectorArgs(match_labels = app_labels),
        replicas = 2,
        template = k8s.core.v1.PodTemplateSpecArgs(
            metadata = k8s.meta.v1.ObjectMetaArgs(labels = app_labels),
            spec = k8s.core.v1.PodSpecArgs(containers = [
                k8s.core.v1.ContainerArgs(name = app_name, image = 'nginx')
            ]),
        ),
    ), opts = pulumi.ResourceOptions(provider = cluster.provider)
)
service = k8s.core.v1.Service(f'{app_name}-svc',
    spec = k8s.core.v1.ServiceSpecArgs(
        type = 'LoadBalancer',
        selector = app_labels,
        ports = [ k8s.core.v1.ServicePortArgs(port = 80) ],
    ), opts = pulumi.ResourceOptions(provider = cluster.provider)
)

# Export the URL for the load balanced service.
pulumi.export('url', service.status.load_balancer.ingress[0].hostname)
# Export the cluster's kubeconfig.
pulumi.export('kubeconfig', cluster.kubeconfig)
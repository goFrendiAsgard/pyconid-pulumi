import pulumi
import pulumi_kubernetes as k8s
from ekscluster import cluster

app_name = 'my-app'
app_labels = { 'app': app_name }

deployment = k8s.apps.v1.Deployment(f'{app_name}-dep',
    spec = k8s.apps.v1.DeploymentSpecArgs(
        replicas = 2,
        selector = k8s.meta.v1.LabelSelectorArgs(
            match_labels = app_labels
        ),
        template = k8s.core.v1.PodTemplateSpecArgs(
            metadata = k8s.meta.v1.ObjectMetaArgs(labels = app_labels),
            spec = k8s.core.v1.PodSpecArgs(
                containers = [
                    k8s.core.v1.ContainerArgs(
                        name = app_name, 
                        image = 'docker.io/gofrendi/sample-app',
                        image_pull_policy='IfNotPresent',
                        resources = k8s.core.v1.ResourceRequirementsArgs(
                            limits={"cpu": "100m", "memory": "100M"},
                            requests={"cpu": "100m", "memory": "100M"}
                        ),
                        env = [
                            k8s.core.v1.EnvVarArgs(name='APP_HTTP_PORT', value='80'),
                            k8s.core.v1.EnvVarArgs(name='APP_RESPONSE', value='Python Everywhere 🐍'),
                        ]
                    )
                ]
            ),
        ),
    ), 
    opts = pulumi.ResourceOptions(
        provider = cluster.provider
    )
)

service = k8s.core.v1.Service(f'{app_name}-svc',
   spec = k8s.core.v1.ServiceSpecArgs(
        type = 'LoadBalancer',
        selector = app_labels,
        ports = [ 
            k8s.core.v1.ServicePortArgs(port = 80) 
        ],
    ), 
    opts = pulumi.ResourceOptions(
        provider = cluster.provider,
        depends_on = [deployment]
    ) 
)
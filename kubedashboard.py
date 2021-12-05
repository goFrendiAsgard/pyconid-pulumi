import pulumi
import pulumi_kubernetes as k8s
from ekscluster import cluster

kube_dashboard = k8s.helm.v3.Chart(
    'kube-dashboard', 
    config=k8s.helm.v3.LocalChartOpts(
        path='./kubernetes-dashboard',
        namespace= 'default',
        values={
            'service': {
                'externalPorts': '8080'
            },
            'resources': {
                'limits': {
                    'cpu': '200m'
                }
            }
        }
    ),
    opts = pulumi.ResourceOptions(
        provider = cluster.provider
    )
)
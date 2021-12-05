import pulumi
from pulumi_kubernetes.helm.v3 import Chart, ChartOpts, LocalChartOpts, FetchOpts
from ekscluster import cluster

# wordpress = Chart(
#     "wpdev",
#     ChartOpts(
#         chart="wordpress",
#         version="9.6.0",
#         fetch_opts=FetchOpts(
#             repo="https://charts.bitnami.com/bitnami",
#         ),
#     ),
#     opts=pulumi.ResourceOptions(provider=cluster.provider),
# )

kube_dashboard = Chart(
    'kube-dashboard', 
    config=LocalChartOpts(
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
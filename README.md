# Pulumi Demo for Pycon ID 2021

This is a show case of pulumi for my talk at PyCon ID 2021 :)

Python Everywhere!!!

In this demo, you will see:

* How to build an EKS cluster
* How to deploy simple nginx app deployment
* How to use your own docker image instead of nginx
* How to deploy existing kubernetes manifest
* How to deploy existing helm chart
* How to destroy everything
* How to not hate yourself

# Building an EKS cluster

First you will need to create a new pulumi project

```bash
# crate new pulumi project
mkdir -p pycon-pulumi
cd pycon-pulumi
pulumi new
# - chooose aws-python to generate a nice boilerplate
# - create a new stack named "dev"

# select stack and set configuration
pulumi stack ls
pulumi stack select dev
pulumi config set aws:region us-east-2
# Note: you can have several stacks (e.g: dev, staging, production)

# activate virtual environment (pulumi created this for you)
# if you clone this repo, you should make ./venv directory manually: 
# - python -m venv ./venv
# - source ./venv/bin/activate
# - pip install -r requirements.txt
source ./venv/bin/activate

# install eks and kubernetes package
pip install pulumi-eks
pip install pulumi-kubernetes

# optionally, you can do this to update your requirements.txt
pip freeze > requirements.txt
```

Now you are ready.

Let's modify your `__main__.py`

```python
import pulumi
import pulumi_eks as eks

# Create an EKS cluster with the default configuration.
cluster = eks.Cluster('my-cluster')

pulumi.export('kubeconfig', cluster.kubeconfig)
```

And invoke:

```bash
pulumi up
```

By invoking

```bash
pulumi stack output kubeconfig
```

you should get a kubeconfig. You can add it to `~/.kube/config` if you want to manage/explore your EKS cluster using kubectl.

# Deploy Simple Nginx App

For the sake of code separability let's move your cluster definition to `ekscluster.py`:

```python
import pulumi_eks as eks

# Create an EKS cluster with the default configuration.
cluster = eks.Cluster('my-cluster')
```

Also, we want to deploy an Nginx app. So, let's put it on `app.py`:

```python
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
                        image = 'nginx',
                        resources = k8s.core.v1.ResourceRequirementsArgs(
                            limits={"cpu": "100m", "memory": "100M"},
                            requests={"cpu": "100m", "memory": "100M"}
                        )
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
```

Finally, let's wrap everything into `__main__.py`

```python
import pulumi
from ekscluster import cluster
from app import deployment, service

# Export the URL for the load balanced service.
pulumi.export('url', service.status.load_balancer.ingress[0].hostname)

# Export the cluster's kubeconfig.
pulumi.export('kubeconfig', cluster.kubeconfig)
```

When you perform

```bash
pulumi up
```

Pulumi will automagically look for every objects imported into your `__main__.py` plus their respective dependencies.

For example, if you modif this line:

```python
from app import deployment, service
```

into


```python
from app import service
```

Your `deployment` is still going to be deployed since your `service` depends on the `deployment`.

But if you remove that line entirely (you need to remove `pulumi.export('url', service.status.load_balancer.ingress[0].hostname)` as well), then your `deployment` and `service` is not going to be deployed.

If they were already there, they will be removed to match your definition.

# Use your own docker image

I've wrote a very simple web app and wrapped it as docker image. You can find the code [here](./sample-app). You can also find the docker image [here](https://hub.docker.com/repository/docker/gofrendi/sample-app).

You can configure the app's behavior by manipulating these two environment variables:

```bash
# HTTP Port
APP_HTTP_PORT=3000
# Default response when you access `/` path using `GET` HTTP method.
APP_RESPONSE="hello world"
```

To run the app locally, you can invoke `./run.sh`.

Now, let's modify our `app.py`

```python
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
```

# Deploy existing kubernetes manifest

Suppose we have existing kubernetes manifest in `./kube-manifest/app.yaml`. You can deploy it using Pulumi as well.

First, create `legacyapp.py`

```python
import pulumi
import pulumi_kubernetes as k8s
from ekscluster import cluster

legacy_app = k8s.yaml.ConfigGroup(
    "legacy",
    files=["./kube-manifest/app.yaml"]
)
```

and modify `__main__.py`

```python
import pulumi
from ekscluster import cluster
from app import deployment, service
from legacyapp import legacy_app

# Export the URL for the load balanced service.
pulumi.export('url', service.status.load_balancer.ingress[0].hostname)

# Export the cluster's kubeconfig.
pulumi.export('kubeconfig', cluster.kubeconfig)
```

# Deploy helm chart

Suppose we have a local chart on `./kubernetes-dashboard`, you can use the existing chart by creating `kubernetesdashboard.py`:

```python
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
```

and modifying `__main__.py`:

```python
import pulumi
from ekscluster import cluster
from app import deployment, service
from legacyapp import legacy_app
from kubedashboard import kube_dashboard

# Export the URL for the load balanced service.
pulumi.export('url', service.status.load_balancer.ingress[0].hostname)

# Export the cluster's kubeconfig.
pulumi.export('kubeconfig', cluster.kubeconfig)
```

# Destroy everything

```bash
pulumi destroy
```

# Not hating yourself

You are awesome, you have survive for so long and you will survive longer!!! 🎉🎉🎉
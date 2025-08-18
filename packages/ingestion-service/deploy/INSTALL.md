# Installation Instructions

This document provides instructions on how to build and push the container images for the ingestion services, and how to deploy the services to a Kubernetes cluster.

## Prerequisites

*   [Podman](https://podman.io/getting-started/installation)
*   [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
*   [Helm](https://helm.sh/docs/intro/install/)
*   A Kubernetes cluster
*   A container registry (e.g., [quay.io](https://quay.io/))

## Building and Pushing Container Images

1.  **Login to your container registry:**

    ```bash
    podman login quay.io
    ```

2.  **Build and push the `ingestion-service-py` image:**

    ```bash
    cd ../ingestion-service-py
    podman build -t quay.io/<your-username>/ingestion-service-py:latest .
    podman push quay.io/<your-username>/ingestion-service-py:latest
    cd ../deploy
    ```



## Deploying to Kubernetes

### Configuration Overview

The Helm charts include sensible defaults for local development but can be customized for different environments:

- **Development (KinD/Minikube)**: Uses ephemeral storage, single replicas, default service names
- **Production (OpenShift/EKS/GKE)**: Requires persistent storage, multiple replicas, custom configurations

### Kafka Connection Options

The ingestion service can connect to Kafka in multiple ways:

1. **Local Kafka** (deployed by same Makefile): Uses auto-generated service names
2. **External Kafka** (different namespace/cluster): Specify custom `KAFKA_HOST` and `KAFKA_PORT`
3. **Cloud Kafka** (AWS MSK, Confluent Cloud, etc.): Use external hostnames and ports

**Key Variables:**
- `KAFKA_HOST`: Kafka bootstrap server hostname (default: auto-generated from `KAFKA_RELEASE_NAME`)
- `KAFKA_PORT`: Kafka port (default: `9092`)
- `KAFKA_RELEASE_NAME`: Only used for local Kafka deployment and hostname generation

### Deployment Scenarios

#### 🚀 **Scenario 1: Quick Local Development (KinD)**

Perfect for local development with minimal configuration:

```bash
# 1. Build and push your image first
cd ../ingestion-service-py
podman build -t quay.io/your-username/ingestion-service-py:dev .
podman push quay.io/your-username/ingestion-service-py:dev
cd ../deploy

# 2. Deploy with your image
make install-kafka
make install-ingestion-py IMAGE_REPOSITORY=quay.io/your-username/ingestion-service-py IMAGE_TAG=dev
```

**What this creates:**
- Kafka cluster: `kafka-kafka` with ephemeral storage
- Service: `kafka-kafka-kafka-bootstrap:9092`
- Single replica, single partition topics
- Ingestion service connects automatically with your custom image

#### 🏢 **Scenario 2: Custom Release Names**

When you need different release names (e.g., multiple environments):

```bash
# Deploy with custom names and your image
make install-kafka KAFKA_RELEASE_NAME=dev-kafka
make install-ingestion-py \
  KAFKA_RELEASE_NAME=dev-kafka \
  INGESTION_PY_RELEASE_NAME=dev-ingestion \
  IMAGE_REPOSITORY=quay.io/your-username/ingestion-service-py \
  IMAGE_TAG=dev-v1.0.0
```

**What this creates:**
- Kafka cluster: `dev-kafka-kafka`  
- Service: `dev-kafka-kafka-kafka-bootstrap:9092`
- Ingestion service connects to the custom Kafka service with your image

#### 🌐 **Scenario 3: Production Deployment**

For production environments requiring persistence and high availability:

```bash
# 1. Update image repository first
# Edit ingestion-service-py/helm/values.yaml:
# image:
#   repository: your-registry.com/ingestion-service-py

# 2. Deploy Kafka with production settings
helm install prod-kafka ./kafka \
  --set kafka.cluster.replicas=3 \
  --set kafka.storage.type=persistent \
  --set kafka.storage.size=10Gi \
  --set kafka.topics.transactions.partitions=3 \
  --set kafka.topics.transactions.replicas=3

# 3. Deploy ingestion service
helm install prod-ingestion ./ingestion-service-py/helm \
  --set kafka.host=prod-kafka-kafka-kafka-bootstrap \
  --set replicaCount=3 \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=128Mi \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi
```

#### 🔧 **Scenario 4: External Kafka Connection**

Connect to an existing Kafka cluster (different namespace, external cluster, or cloud service):

```bash
# Connect to Kafka in different namespace
make install-ingestion-py \
  KAFKA_HOST=my-kafka-kafka-bootstrap.kafka-namespace.svc.cluster.local \
  KAFKA_PORT=9092

# Connect to external Kafka cluster
make install-ingestion-py \
  KAFKA_HOST=kafka.example.com \
  KAFKA_PORT=9092

# Connect to cloud Kafka service
make install-ingestion-py \
  KAFKA_HOST=my-cluster.kafka.us-east-1.amazonaws.com \
  KAFKA_PORT=9092
```

#### 🔧 **Scenario 5: Cross-Namespace Deployment**

When Kafka and ingestion service are in different namespaces:

```bash
# Deploy Kafka in kafka namespace
kubectl create namespace kafka
helm install kafka ./kafka --namespace kafka

# Deploy ingestion service in apps namespace using FQDN
kubectl create namespace apps
make install-ingestion-py \
  INGESTION_PY_NAMESPACE=apps \
  KAFKA_HOST=kafka-kafka-kafka-bootstrap.kafka.svc.cluster.local \
  KAFKA_PORT=9092
```

### Environment-Specific Values Files

For complex deployments, create environment-specific values files:

**`values-dev.yaml`:**
```yaml
kafka:
  cluster:
    replicas: 1
  storage:
    type: ephemeral
```

**`values-prod.yaml`:**
```yaml
kafka:
  cluster:
    replicas: 3
  storage:
    type: persistent
    size: 20Gi
  topics:
    transactions:
      partitions: 6
      replicas: 3
```

Then deploy with:
```bash
helm install kafka ./kafka -f values-prod.yaml
```

### Quick Start

For most users, the simple approach works perfectly:

1.  **Build and push your container image** (required for deployment):
    ```bash
    # Build and push to your container registry
    cd ../ingestion-service-py
    podman build -t quay.io/your-username/ingestion-service-py:latest .
    podman push quay.io/your-username/ingestion-service-py:latest
    cd ../deploy
    ```

2.  **Deploy Kafka:**
    ```bash
    make install-kafka
    ```

3.  **Deploy the ingestion service with your image:**
    ```bash
    make install-ingestion-py IMAGE_REPOSITORY=quay.io/your-username/ingestion-service-py IMAGE_TAG=latest
    ```

## Testing the Ingestion Service

To test the ingestion service, you can use `kubectl port-forward` to forward a local port to the service running in the cluster.

1.  **Port-forward the `ingestion-service-py`:**

    ```bash
    kubectl port-forward svc/ingestion-py 8080:80
    ```

Now you can send requests to `localhost:8080` to test the Python service.

You can use the provided `bulk_ingest.py` script to send test transactions.

```bash
python ../scripts/bulk_ingest.py --service ingestion-service-py
```

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

1.  **Update the image repository in the `values.yaml` file:**

    Before deploying, you need to update the `image.repository` value in the following file to point to your container registry:

    *   `ingestion-service-py/helm/values.yaml`

2.  **Deploy Kafka:**

    ```bash
    make install-kafka
    ```

3.  **Deploy the ingestion service:**

    ```bash
    make install-ingestion-py
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

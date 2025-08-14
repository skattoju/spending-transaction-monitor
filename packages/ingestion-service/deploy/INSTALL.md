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

3.  **Build and push the `ingestion-service-ts` image:**

    ```bash
    cd ../ingestion-service-ts
    podman build -t quay.io/<your-username>/ingestion-service-ts:latest .
    podman push quay.io/<your-username>/ingestion-service-ts:latest
    cd ../deploy
    ```

## Deploying to Kubernetes

1.  **Update the image repository in the `values.yaml` files:**

    Before deploying, you need to update the `image.repository` value in the following files to point to your container registry:

    *   `ingestion-service-py/helm/values.yaml`
    *   `ingestion-service-ts/helm/values.yaml`

2.  **Deploy Kafka:**

    ```bash
    make install-kafka
    ```

3.  **Deploy the ingestion services:**

    ```bash
    make install-ingestion-py
    make install-ingestion-ts
    ```

## Testing the Ingestion Services

To test the ingestion services, you can use `kubectl port-forward` to forward a local port to the service running in the cluster.

1.  **Port-forward the `ingestion-service-py`:**

    ```bash
    kubectl port-forward svc/ingestion-py 8080:80
    ```

2.  **Port-forward the `ingestion-service-ts`:**

    ```bash
    kubectl port-forward svc/ingestion-ts 8081:80
    ```

Now you can send requests to `localhost:8080` to test the Python service, and `localhost:8081` to test the TypeScript service.

You can use the provided `bulk_ingest.py` script to send test transactions.

```bash
python ../scripts/bulk_ingest.py --service <service-name>
```

Replace `<service-name>` with either `ingestion-service-py` or `ingestion-service-ts`.

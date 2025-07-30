# TypeScript Ingestion Service

This service is a TypeScript-based implementation of the transaction ingestion service. It uses Express to create a REST API and `kafkajs` to produce messages to a Kafka topic.

## Local Development

**Note:** The service requires a running Kafka instance. For local development, you can use the provided Docker Compose file to start Kafka: `docker-compose -f ../deploy/kafka/compose.yaml up -d`

To run the service locally, you will need to have Node.js and npm installed.

1.  **Install the dependencies:**

    ```bash
    npm install
    ```

2.  **Run the service:**

    The service will be available at `http://localhost:3000`.

    ```bash
    export KAFKA_HOST=localhost
    export KAFKA_PORT=9092
    npx ts-node src/index.ts
    ```

3.  **Run the tests:**

    ```bash
    npm test
    ```

## Building and Pushing the Container Image

1.  **Login to your container registry (e.g., quay.io):**

    ```bash
    docker login quay.io
    ```

2.  **Build and push the image:**

    Replace `<your-username>` with your container registry username.

    ```bash
    docker build -t quay.io/<your-username>/ingestion-service-ts:latest .
    docker push quay.io/<your-username>/ingestion-service-ts:latest
    ```

## Deployment

The ingestion service is deployed to Kubernetes using Helm. For instructions on how to deploy Kafka, see the main `README.md` file.

1.  **Update the `values.yaml` file:**

    Before deploying, you need to update the `image.repository` value in `../deploy/ingestion-service-ts/helm/values.yaml` to point to your container registry.

2.  **Deploy the `ingestion-service-ts`:**

    ```bash
    make -C ../deploy install-ingestion-ts
    ```

## Testing with cURL

1.  **Port-forward the service:**

    ```bash
    kubectl port-forward svc/ingestion-ts 8081:80
    ```

2.  **Send a test transaction:**

    ```bash
    curl -X POST "http://localhost:8081/transactions/" \
    -H "Content-Type: application/json" \
    -d '{
        "user_id": 123,
        "card_id": 456,
        "amount": 78.90,
        "description": "Test transaction"
    }'
    ```

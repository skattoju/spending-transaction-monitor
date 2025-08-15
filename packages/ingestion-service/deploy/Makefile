# Makefile for deploying the ingestion service and Kafka
# 
# Usage examples:
#   make install-kafka                                    # Uses default values
#   make install-kafka KAFKA_RELEASE_NAME=my-kafka       # Custom release name
#   make install-ingestion-py                             # Uses defaults (connects to "kafka" release)
#   make install-ingestion-py KAFKA_RELEASE_NAME=my-kafka # Connects to custom Kafka release
#   make install-ingestion-py IMAGE_REPOSITORY=quay.io/myuser/ingestion-py IMAGE_TAG=v1.0.0 # Custom image

# Default values - safe for local development with KinD
KAFKA_RELEASE_NAME ?= kafka
INGESTION_PY_RELEASE_NAME ?= ingestion-py
KAFKA_NAMESPACE ?= default
INGESTION_PY_NAMESPACE ?= default

# Image configuration - override these for your registry
IMAGE_REPOSITORY ?= quay.io/your-username/ingestion-service-py
IMAGE_TAG ?= latest

# Targets
install-kafka:
	helm install $(KAFKA_RELEASE_NAME) ./kafka --namespace $(KAFKA_NAMESPACE)

install-ingestion-py:
	helm install $(INGESTION_PY_RELEASE_NAME) ./ingestion-service-py/helm \
		--namespace $(INGESTION_PY_NAMESPACE) \
		--set kafka.host=$(KAFKA_RELEASE_NAME)-kafka-kafka-bootstrap \
		--set kafka.port=9092 \
		--set image.repository=$(IMAGE_REPOSITORY) \
		--set image.tag=$(IMAGE_TAG)

uninstall-kafka:
	helm uninstall $(KAFKA_RELEASE_NAME) --namespace $(KAFKA_NAMESPACE)

uninstall-ingestion-py:
	helm uninstall $(INGESTION_PY_RELEASE_NAME) --namespace $(INGESTION_PY_NAMESPACE)

.PHONY: install-kafka install-ingestion-py uninstall-kafka uninstall-ingestion-py

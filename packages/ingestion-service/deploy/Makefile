# Makefile for deploying the ingestion service and Kafka
# 
# Usage examples:
#   make install-kafka                                    # Uses default values
#   make install-kafka KAFKA_RELEASE_NAME=my-kafka       # Custom release name
#   make install-ingestion-py                             # Uses defaults (connects to "kafka" release)
#   make install-ingestion-py KAFKA_RELEASE_NAME=my-kafka # Connects to custom Kafka release

# Default values - safe for local development with KinD
KAFKA_RELEASE_NAME ?= kafka
INGESTION_PY_RELEASE_NAME ?= ingestion-py
KAFKA_NAMESPACE ?= default
INGESTION_PY_NAMESPACE ?= default

# Targets
install-kafka:
	helm install $(KAFKA_RELEASE_NAME) ./kafka --namespace $(KAFKA_NAMESPACE)

install-ingestion-py:
	helm install $(INGESTION_PY_RELEASE_NAME) ./ingestion-service-py/helm \
		--namespace $(INGESTION_PY_NAMESPACE) \
		--set kafka.host=$(KAFKA_RELEASE_NAME)-kafka-kafka-bootstrap \
		--set kafka.port=9092

uninstall-kafka:
	helm uninstall $(KAFKA_RELEASE_NAME) --namespace $(KAFKA_NAMESPACE)

uninstall-ingestion-py:
	helm uninstall $(INGESTION_PY_RELEASE_NAME) --namespace $(INGESTION_PY_NAMESPACE)

.PHONY: install-kafka install-ingestion-py uninstall-kafka uninstall-ingestion-py

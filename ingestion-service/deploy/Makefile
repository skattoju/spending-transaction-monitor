# Makefile for deploying the ingestion services and Kafka

# Default values
KAFKA_RELEASE_NAME ?= kafka
INGESTION_PY_RELEASE_NAME ?= ingestion-py
INGESTION_TS_RELEASE_NAME ?= ingestion-ts
KAFKA_NAMESPACE ?= default
INGESTION_PY_NAMESPACE ?= default
INGESTION_TS_NAMESPACE ?= default

# Targets
install-kafka:
	helm install $(KAFKA_RELEASE_NAME) ./kafka --namespace $(KAFKA_NAMESPACE)

install-ingestion-py:
	helm install $(INGESTION_PY_RELEASE_NAME) ./ingestion-service-py/helm \
		--namespace $(INGESTION_PY_NAMESPACE) \
		--set kafka.host=$(KAFKA_RELEASE_NAME)-kafka-bootstrap \
		--set kafka.port=9092

install-ingestion-ts:
	helm install $(INGESTION_TS_RELEASE_NAME) ./ingestion-service-ts/helm \
		--namespace $(INGESTION_TS_NAMESPACE) \
		--set kafka.host=$(KAFKA_RELEASE_NAME)-kafka-bootstrap \
		--set kafka.port=9092

uninstall-kafka:
	helm uninstall $(KAFKA_RELEASE_NAME) --namespace $(KAFKA_NAMESPACE)

uninstall-ingestion-py:
	helm uninstall $(INGESTION_PY_RELEASE_NAME) --namespace $(INGESTION_PY_NAMESPACE)

uninstall-ingestion-ts:
	helm uninstall $(INGESTION_TS_RELEASE_NAME) --namespace $(INGESTION_TS_NAMESPACE)

.PHONY: install-kafka install-ingestion-py install-ingestion-ts uninstall-kafka uninstall-ingestion-py uninstall-ingestion-ts

# Makefile for deploying the ingestion service
# 
# Usage examples:
#   make install-ingestion-py                             # Uses default values
#   make install-ingestion-py IMAGE_REPOSITORY=quay.io/myuser/ingestion-py IMAGE_TAG=v1.0.0 # Custom image

# Default values - safe for local development with KinD
INGESTION_PY_RELEASE_NAME ?= ingestion-py
INGESTION_PY_NAMESPACE ?= default

# Image configuration - override these for your registry
IMAGE_REPOSITORY ?= quay.io/your-username/ingestion-service-py
IMAGE_TAG ?= latest


# Targets

install-ingestion-py:
	helm install $(INGESTION_PY_RELEASE_NAME) ./ingestion-service-py/helm \
		--namespace $(INGESTION_PY_NAMESPACE) \
		--set image.repository=$(IMAGE_REPOSITORY) \
		--set image.tag=$(IMAGE_TAG)


uninstall-ingestion-py:
	helm uninstall $(INGESTION_PY_RELEASE_NAME) --namespace $(INGESTION_PY_NAMESPACE)

.PHONY: install-ingestion-py uninstall-ingestion-py

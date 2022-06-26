#!/bin/sh
set -eu
PROJECT_ID=my-project2-303004
CLUSTER_NAME=fast-api-terraform-cluster
SERVICE_NAME=fast-api-server
ZONE=us-central1-b

gcloud container clusters get-credentials ${CLUSTER_NAME} --project ${PROJECT_ID} --region ${ZONE}
IP_ADDRESS_PROD=`kubectl describe service ${SERVICE_NAME} -n prod | grep "LoadBalancer Ingress" | awk '{print $3}'`
PORT=5000
IP_ADDRESS_DEV=`kubectl describe service ${SERVICE_NAME} -n dev | grep "LoadBalancer Ingress" | awk '{print $3}'`
PORT=5000

# health check
echo "[prod]"
curl http://${IP_ADDRESS_PROD}:${PORT}/health

echo "[dev]"
curl http://${IP_ADDRESS_DEV}:${PORT}/health

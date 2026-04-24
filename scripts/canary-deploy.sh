#!/bin/bash
# Canary Deploy: постепенно увеличиваем трафик на новую версию.
# На каждом шаге проверяем Error Rate — если > 5%, откатываем.
# Использование: bash scripts/canary-deploy.sh

set -e

PROMETHEUS_URL="${PROMETHEUS_URL:-http://monitoring-kube-prometheus-prometheus:9090}"
ERROR_THRESHOLD=5

echo "=== Canary Deploy ==="

# 1. Применяем манифест
echo "[1] Разворачиваю canary..."
kubectl apply -f k8s/canary/deployment.yaml
kubectl rollout status deployment/webapp-canary --timeout=120s

# 2. Постепенно увеличиваем вес
for WEIGHT in 10 25 50 75 100; do
  echo "[Canary] Устанавливаю вес: ${WEIGHT}%"
  kubectl annotate ingress webapp-ingress \
    nginx.ingress.kubernetes.io/canary-weight="$WEIGHT" --overwrite

  # Ждём 60 секунд, чтобы собрать метрики
  echo "[Canary] Жду 60 секунд для сбора метрик..."
  sleep 60

  # Проверяем Error Rate через Prometheus
  ERROR_RATE=$(curl -s "${PROMETHEUS_URL}/api/v1/query" \
    --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[1m]) / rate(http_requests_total[1m]) * 100' \
    | jq -r '.data.result[0].value[1] // "0"')

  echo "[Canary] Error Rate: ${ERROR_RATE}%"

  if (( $(echo "$ERROR_RATE > $ERROR_THRESHOLD" | bc -l) )); then
    echo "[Canary] Error Rate ${ERROR_RATE}% > ${ERROR_THRESHOLD}%. ОТКАТ!"
    kubectl delete -f k8s/canary/deployment.yaml
    exit 1
  fi
done

# 3. Canary прошёл — удаляем stable, canary становится основным
echo "=== Canary успешно завершён, 100% трафика на новой версии ==="

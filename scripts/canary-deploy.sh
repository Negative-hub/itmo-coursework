#!/bin/bash
# Canary-эксперимент: постепенно увеличиваем трафик на новую версию.
# Запускать через 5 минут после старта k6.
# Canary-поды уже должны быть развёрнуты.

set -e

echo "=== Canary Deploy ==="
echo "DEPLOY START: $(date)"

echo "Разворачиваю stable и canary среды..."
kubectl apply -f k8s/canary/deployment.yaml
kubectl rollout status deployment/webapp-canary --timeout=180s

# 2. Постепенно увеличиваем вес
for WEIGHT in 10 25 50 75 100; do
  echo "[Canary] Устанавливаю вес: ${WEIGHT}%"
  kubectl annotate ingress webapp-ingress \
    nginx.ingress.kubernetes.io/canary-weight="$WEIGHT" --overwrite
  echo "[Canary] Вес: ${WEIGHT}% — $(date)"
  
  if [ "$WEIGHT" -lt 100 ]; then
    echo "[Canary] Жду 60 секунд..."
    sleep 60
  fi
done

echo "DEPLOY END: $(date)"
echo "=== Canary завершён, 100% трафика на новой версии ==="

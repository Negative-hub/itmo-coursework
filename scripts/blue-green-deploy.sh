#!/bin/bash
# Blue-Green Deploy: разворачиваем green, переключаем трафик с blue на green.
# Использование: bash scripts/blue-green-deploy.sh

set -e

echo "=== Blue-Green Deploy ==="

# 1. Применяем манифест (оба Deployment + Service)
echo "[1/3] Разворачиваю blue и green среды..."
kubectl apply -f k8s/blue-green/deployment.yaml

# 2. Ждём готовности зелёной среды
echo "[2/3] Жду готовности webapp-green..."
kubectl rollout status deployment/webapp-green --timeout=120s

# 3. Переключаем трафик на green
echo "[3/3] Переключаю трафик на green..."
kubectl patch svc webapp-service \
  -p '{"spec":{"selector":{"color":"green"}}}'

echo "=== Трафик переключён на green ==="

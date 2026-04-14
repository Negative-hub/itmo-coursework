#!/bin/bash
# Запуск одного эксперимента для указанной стратегии.
# Использование: bash scripts/run-experiment.sh <стратегия> <номер_запуска>
# Пример: bash scripts/run-experiment.sh recreate 1

set -e

STRATEGY=${1:?"Укажи стратегию: recreate | rolling | blue-green | canary"}
RUN_NUMBER=${2:?"Укажи номер запуска: 1-5"}
BASE_URL=${BASE_URL:?"Укажи BASE_URL (внешний IP Ingress)"}
RESULTS_DIR="results/${STRATEGY}/run-${RUN_NUMBER}"

echo "==========================================="
echo "  Стратегия: ${STRATEGY}"
echo "  Запуск:    ${RUN_NUMBER} из 5"
echo "  URL:       ${BASE_URL}"
echo "==========================================="

# Создаём папку для результатов
mkdir -p "$RESULTS_DIR"

# --- Шаг 1: Очистка ---
echo "[1/6] Очищаю предыдущий деплой..."
kubectl delete deployment webapp webapp-blue webapp-green webapp-stable webapp-canary 2>/dev/null || true
kubectl delete ingress webapp-ingress webapp-canary-ingress 2>/dev/null || true
kubectl delete svc webapp-service webapp-stable-service webapp-canary-service 2>/dev/null || true
sleep 10

# --- Шаг 2: Деплой v1.0.0 (стабильная версия) ---
echo "[2/6] Разворачиваю стабильную версию v1.0.0..."
# Для всех стратегий сначала ставим через rolling (как начальное состояние)
kubectl apply -f k8s/rolling/deployment.yaml
kubectl rollout status deployment/webapp --timeout=120s
echo "v1.0.0 развёрнута. Жду 30 секунд для прогрева..."
sleep 30

# --- Шаг 3: Запуск k6 (нагрузка + health-check) в фоне ---
echo "[3/6] Запускаю k6 load-test и health-check..."
k6 run --out json="${RESULTS_DIR}/load-test.json" \
  -e BASE_URL="${BASE_URL}" \
  k6/load-test.js > "${RESULTS_DIR}/load-test.log" 2>&1 &
LOAD_PID=$!

k6 run --out json="${RESULTS_DIR}/health-check.json" \
  -e BASE_URL="${BASE_URL}" \
  k6/health-check.js > "${RESULTS_DIR}/health-check.log" 2>&1 &
HEALTH_PID=$!

# --- Шаг 4: Ждём 5 минут (этап подготовки), затем запускаем деплой v1.1.0 ---
echo "[4/6] Жду 5 минут (этап подготовки)..."
sleep 300

echo "[5/6] Запускаю деплой v1.1.0 (стратегия: ${STRATEGY})..."
DEPLOY_START=$(date +%s)

case "$STRATEGY" in
  recreate)
    # Меняем тег образа и применяем
    sed -i.bak "s|v1.0.0|v1.1.0|g" k8s/recreate/deployment.yaml
    kubectl apply -f k8s/recreate/deployment.yaml
    kubectl rollout status deployment/webapp --timeout=300s
    # Восстанавливаем файл
    mv k8s/recreate/deployment.yaml.bak k8s/recreate/deployment.yaml
    ;;
  rolling)
    sed -i.bak "s|v1.0.0|v1.1.0|g" k8s/rolling/deployment.yaml
    kubectl apply -f k8s/rolling/deployment.yaml
    kubectl rollout status deployment/webapp --timeout=300s
    mv k8s/rolling/deployment.yaml.bak k8s/rolling/deployment.yaml
    ;;
  blue-green)
    bash scripts/blue-green-deploy.sh
    ;;
  canary)
    bash scripts/canary-deploy.sh
    ;;
esac

DEPLOY_END=$(date +%s)
DEPLOY_TIME=$((DEPLOY_END - DEPLOY_START))
echo "Деплой завершён за ${DEPLOY_TIME} секунд"
echo "${DEPLOY_TIME}" > "${RESULTS_DIR}/deploy-time.txt"

# --- Шаг 6: Ждём завершения k6 ---
echo "[6/6] Жду завершения k6..."
wait $LOAD_PID
wait $HEALTH_PID

echo "==========================================="
echo "  Эксперимент завершён!"
echo "  Результаты: ${RESULTS_DIR}/"
echo "  Время деплоя: ${DEPLOY_TIME}с"
echo "==========================================="

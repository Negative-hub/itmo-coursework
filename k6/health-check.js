import http from 'k6/http';
import { check } from 'k6';
import { Rate, Counter, Trend } from 'k6/metrics';

// === Кастомные метрики для измерения простоя ===
const healthErrors = new Rate('health_errors');         // Доля неудачных проверок
const healthFailCount = new Counter('health_fail_count'); // Абсолютное число сбоев
const healthLatency = new Trend('health_latency');      // Задержка ответа health

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  // Запускаем на 20 минут (покрывает все три этапа эксперимента)
  // 1 пользователь, но с очень частыми запросами (каждые 100 мс)
  scenarios: {
    health_monitor: {
      executor: 'constant-arrival-rate',
      rate: 10,              // 10 запросов в секунду = каждые 100 мс
      timeUnit: '1s',
      duration: '20m',
      preAllocatedVUs: 2,
      maxVUs: 5,
    },
  },

  thresholds: {
    'health_errors': ['rate<0.05'],  // Ошибок < 5%
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/api/health`, {
    timeout: '3s',  // Таймаут 3 секунды — если не ответил, считаем сбоем
  });

  const isOk = check(res, {
    'health — статус 200': (r) => r.status === 200,
    'health — ответ < 1с': (r) => r.timings.duration < 1000,
  });

  // Фиксируем ошибку
  if (!isOk) {
    healthFailCount.add(1);
  }

  healthErrors.add(!isOk);
  healthLatency.add(res.timings.duration);
}

// === После теста выводим сводку ===
export function handleSummary(data) {
  const totalChecks = data.metrics.health_errors ? data.metrics.health_errors.values.passes + data.metrics.health_errors.values.fails : 0;
  const failedChecks = data.metrics.health_fail_count ? data.metrics.health_fail_count.values.count : 0;

  // Каждая проверка = 100 мс, значит время простоя = failedChecks * 0.1 секунды
  const downtimeSeconds = (failedChecks * 0.1).toFixed(1);

  console.log(`\n=== РЕЗУЛЬТАТ ===`);
  console.log(`Всего проверок: ${totalChecks}`);
  console.log(`Неудачных: ${failedChecks}`);
  console.log(`Время простоя: ~${downtimeSeconds} секунд`);
  console.log(`=================\n`);

  return {
    stdout: JSON.stringify({
      total_checks: totalChecks,
      failed_checks: failedChecks,
      downtime_seconds: parseFloat(downtimeSeconds),
    }, null, 2),
  };
}

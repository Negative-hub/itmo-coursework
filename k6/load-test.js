import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// === Кастомные метрики ===
// Они будут экспортированы в Prometheus для анализа в Grafana
const errorRate = new Rate('errors');
const termsLatency = new Trend('terms_latency');
const createLatency = new Trend('create_latency');

// === Конфигурация ===
// BASE_URL задаётся при запуске: k6 run -e BASE_URL=http://... load-test.js
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// === Этапы эксперимента (из методики, глава 2) ===
export const options = {
  stages: [
    // Этап 1: Подготовка — 100 пользователей, 5 минут
    { duration: '1m', target: 100 },   // разгон до 100
    { duration: '4m', target: 100 },   // удержание 100

    // Этап 2: Развёртывание — 500 пользователей, 5 минут
    // (деплой запускается вручную в начале этого этапа)
    { duration: '2m', target: 500 },   // разгон до 500
    { duration: '3m', target: 500 },   // удержание 500

    // Этап 3: Стабилизация — 100 пользователей, 10 минут
    { duration: '2m', target: 100 },   // снижение до 100
    { duration: '8m', target: 100 },   // удержание 100
  ],

  // Пороговые значения — если превышены, тест считается проваленным
  thresholds: {
    'http_req_duration': ['p(99)<2000'],   // P99 < 2 секунд
    'errors': ['rate<0.1'],                 // Ошибок < 10%
  },
};

// === Тело теста ===
// Каждый виртуальный пользователь в цикле выполняет:
// - с вероятностью 80% — GET /api/terms (чтение)
// - с вероятностью 20% — POST /api/terms (запись)
export default function () {
  const random = Math.random();

  if (random < 0.8) {
    // === GET /api/terms — чтение (80% запросов) ===
    const res = http.get(`${BASE_URL}/api/terms`);

    check(res, {
      'GET /api/terms — статус 200': (r) => r.status === 200,
    });

    errorRate.add(res.status >= 500);
    termsLatency.add(res.timings.duration);

  } else {
    // === POST /api/terms — запись (20% запросов) ===
    const payload = JSON.stringify({
      name: `term-${Date.now()}-${Math.floor(Math.random() * 100000)}`,
      description: 'Тестовый термин для нагрузочного тестирования',
      source_url: 'https://example.com/test',
    });

    const params = {
      headers: { 'Content-Type': 'application/json' },
    };

    const res = http.post(`${BASE_URL}/api/terms`, payload, params);

    check(res, {
      'POST /api/terms — статус 201': (r) => r.status === 201,
    });

    errorRate.add(res.status >= 500);
    createLatency.add(res.timings.duration);
  }

  // Пауза 0.5-1.5 секунды между запросами (имитация реального пользователя)
  sleep(Math.random() + 0.5);
}

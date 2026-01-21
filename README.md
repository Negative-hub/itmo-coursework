# ITMO Coursework

Полноценное веб-приложение для визуализации семантического графа терминов веб-разработки.

## Архитектура

- **Бэкенд**: FastAPI + SQLite (REST API)
- **Фронтенд**: Vue.js 3 + Vite + Cytoscape.js
- **Веб-сервер**: Nginx (для фронтенда)
- **Контейнеризация**: Docker + Docker Compose

## Запуск проекта

```bash
# Клонируйте проект
git clone https://github.com/Negative-hub/itmo-coursework
cd itmo-coursework

# Запустите все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```
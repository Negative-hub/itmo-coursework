# Стадия 1: установка зависимостей
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Стадия 2: финальный образ (копируем только нужное)
FROM python:3.11-slim
WORKDIR /app

# Копируем установленные пакеты из первой стадии
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем исходный код приложения
COPY ./app ./app

EXPOSE 8000

# Запуск без --reload (продакшен-режим)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

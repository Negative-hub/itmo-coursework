FROM python:3.11-slim

WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для базы данных, если её нет
RUN mkdir -p ./instance

# Копирование исходного кода
COPY ./app ./app
COPY ./instance ./instance

# Открываем порт
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
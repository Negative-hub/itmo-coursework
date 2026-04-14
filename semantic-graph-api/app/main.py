import os
import json
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import redis

from app import routes, models, schemas
from app.database import engine, get_db, Base

# Версия приложения — задаётся при деплое через переменную окружения.
# По ней мы определяем, какая версия обслуживает запрос
# (важно для Blue-Green и Canary стратегий).
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# Подключение к Redis — хост задаётся через переменную окружения.
REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

# Время жизни кэша в секундах
CACHE_TTL = 60

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Создаём приложение FastAPI
app = FastAPI(
    title="Semantic Graph API",
    description="API для семантического графа терминов веб-разработки",
    version=APP_VERSION
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    """
    Эндпоинт проверки здоровья.
    Проверяет доступность PostgreSQL и Redis.
    Используется для:
    - readiness/liveness probes в Kubernetes
    - измерения Downtime в k6-сценариях
    """
    try:
        # Проверяем PostgreSQL
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"PostgreSQL недоступен: {e}")

    try:
        # Проверяем Redis
        redis_client.ping()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis недоступен: {e}")

    return {"status": "ok", "version": APP_VERSION}


@app.get("/api/terms", response_model=List[schemas.Term])
def read_terms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получить список всех терминов.
    Ответ кэшируется в Redis на 60 секунд.
    """
    cache_key = f"terms:skip={skip}:limit={limit}"

    # Пробуем взять из кэша
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Если кэша нет — идём в PostgreSQL
    terms = routes.get_terms(db, skip=skip, limit=limit)

    # Сохраняем в кэш
    terms_data = [schemas.Term.model_validate(t).model_dump() for t in terms]
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(terms_data))

    return terms


@app.post("/api/terms", response_model=schemas.Term, status_code=201)
def create_term(term: schemas.TermCreate, db: Session = Depends(get_db)):
    """
    Создать новый термин.
    После создания сбрасываем кэш Redis,
    чтобы GET /api/terms вернул актуальные данные.
    """
    db_term = routes.create_term(db, term)

    # Инвалидируем кэш — удаляем все ключи, начинающиеся с "terms:"
    for key in redis_client.scan_iter("terms:*"):
        redis_client.delete(key)

    return db_term


@app.get("/api/graph", response_model=schemas.GraphResponse)
def get_full_graph(db: Session = Depends(get_db)):
    """
    Получить полный граф для визуализации.
    """
    terms, relationships = routes.get_full_graph(db)

    nodes = []
    for term in terms:
        nodes.append({
            "data": {
                "id": str(term.id),
                "label": term.name,
                "name": term.name,
                "description": term.description,
                "source_url": term.source_url
            }
        })

    edges = []
    edge_id = 1
    for rel in relationships:
        edges.append({
            "data": {
                "id": f"e{edge_id}",
                "source": str(rel.parent_id),
                "target": str(rel.child_id),
                "label": rel.relationship_type,
                "type": rel.relationship_type
            }
        })
        edge_id += 1

    return {"nodes": nodes, "edges": edges}


@app.on_event("startup")
async def startup_event():
    """
    Инициализация базы данных при старте приложения.
    """
    from app.init_db import init_database
    init_database()

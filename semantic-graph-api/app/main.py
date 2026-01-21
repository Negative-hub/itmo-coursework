from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app import routes, models, schemas
from app.database import engine, get_db

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

# Создаем приложение FastAPI
app = FastAPI(
    title="Semantic Graph API",
    description="API для семантического графа терминов веб-разработки",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Semantic Graph API",
        "endpoints": {
            "terms": "/api/terms",
            "term_by_id": "/api/terms/{id}",
            "graph": "/api/graph"
        }
    }

@app.get("/api/terms", response_model=List[schemas.Term])
def read_terms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получить список всех терминов с пагинацией
    """
    terms = routes.get_terms(db, skip=skip, limit=limit)
    return terms

@app.get("/api/terms/{term_id}", response_model=schemas.TermWithRelationships)
def read_term(term_id: int, db: Session = Depends(get_db)):
    """
    Получить термин по ID со всеми связанными терминами
    """
    db_term = routes.get_term(db, term_id=term_id)
    if db_term is None:
        raise HTTPException(status_code=404, detail="Термин не найден")
    
    # Получаем связи
    relationships = routes.get_relationships_by_term(db, term_id)
    
    # Формируем ответ
    term_dict = {
        "id": db_term.id,
        "name": db_term.name,
        "description": db_term.description,
        "source_url": db_term.source_url,
        "influences": [],
        "influenced_by": [],
        "relationship_types": []
    }
    
    # Собираем связанные термины
    for rel in relationships:
        if rel.parent_id == term_id:
            # Текущий термин влияет на другой
            influenced_term = routes.get_term(db, rel.child_id)
            if influenced_term:
                term_dict["influences"].append({
                    "id": influenced_term.id,
                    "name": influenced_term.name,
                    "description": influenced_term.description,
                    "source_url": influenced_term.source_url
                })
        elif rel.child_id == term_id:
            # На текущий термин влияет другой
            influencer_term = routes.get_term(db, rel.parent_id)
            if influencer_term:
                term_dict["influenced_by"].append({
                    "id": influencer_term.id,
                    "name": influencer_term.name,
                    "description": influencer_term.description,
                    "source_url": influencer_term.source_url
                })
        
        term_dict["relationship_types"].append(rel.relationship_type)
    
    # Убираем дубликаты
    term_dict["relationship_types"] = list(set(term_dict["relationship_types"]))
    
    return term_dict

@app.get("/api/graph", response_model=schemas.GraphResponse)
def get_full_graph(db: Session = Depends(get_db)):
    """
    Получить полный граф для визуализации в Cytoscape.js
    """
    terms, relationships = routes.get_full_graph(db)
    
    # Формируем узлы
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
    
    # Формируем связи
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
    Инициализация базы данных при старте приложения
    """
    from .init_db import init_database
    init_database()
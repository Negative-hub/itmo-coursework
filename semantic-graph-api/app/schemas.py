from pydantic import BaseModel
from typing import List

# Схемы для терминов
class TermBase(BaseModel):
    name: str
    description: str
    source_url: str

class TermCreate(TermBase):
    pass

class Term(TermBase):
    id: int
    
    class Config:
        from_attributes = True

# Схемы для связей
class RelationshipBase(BaseModel):
    parent_id: int
    child_id: int
    relationship_type: str

class RelationshipCreate(RelationshipBase):
    pass

class Relationship(RelationshipBase):
    id: int
    
    class Config:
        from_attributes = True

# Схемы для ответов с связями
class TermWithRelationships(Term):
    influences: List["Term"] = []
    influenced_by: List["Term"] = []
    relationship_types: List[str] = []

# Схема для полного графа
class GraphNode(BaseModel):
    data: dict
    
    class Config:
        from_attributes = True

class GraphEdge(BaseModel):
    data: dict
    
    class Config:
        from_attributes = True

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
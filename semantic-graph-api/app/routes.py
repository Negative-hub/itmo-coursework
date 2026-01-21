from app import models, schemas
from sqlalchemy.orm import Session
from sqlalchemy import or_

def get_term(db: Session, term_id: int):
    return db.query(models.Term).filter(models.Term.id == term_id).first()

def get_terms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Term).offset(skip).limit(limit).all()

def create_term(db: Session, term: schemas.TermCreate):
    db_term = models.Term(
        name=term.name,
        description=term.description,
        source_url=term.source_url
    )
    db.add(db_term)
    db.commit()
    db.refresh(db_term)
    return db_term

def create_relationship(db: Session, relationship: schemas.RelationshipCreate):
    db_relationship = models.TermRelationship(
        parent_id=relationship.parent_id,
        child_id=relationship.child_id,
        relationship_type=relationship.relationship_type
    )
    db.add(db_relationship)
    db.commit()
    db.refresh(db_relationship)
    return db_relationship

def get_relationships_by_term(db: Session, term_id: int):
    return db.query(models.TermRelationship).filter(
        or_(
            models.TermRelationship.parent_id == term_id,
            models.TermRelationship.child_id == term_id
        )
    ).all()

def get_full_graph(db: Session):
    # Получаем все термины
    terms = db.query(models.Term).all()
    
    # Получаем все связи
    relationships = db.query(models.TermRelationship).all()
    
    return terms, relationships
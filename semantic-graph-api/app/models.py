from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Term(Base):
    __tablename__ = "terms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=False)
    
    # Связи с другими терминами
    dependencies = relationship(
        "TermRelationship",
        foreign_keys="TermRelationship.parent_id",
        back_populates="parent"
    )
    
    dependents = relationship(
        "TermRelationship",
        foreign_keys="TermRelationship.child_id",
        back_populates="child"
    )

class TermRelationship(Base):
    __tablename__ = "term_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # например: "influences", "depends_on", "improves"
    
    parent = relationship("Term", foreign_keys=[parent_id], back_populates="dependencies")
    child = relationship("Term", foreign_keys=[child_id], back_populates="dependents")
"""
Category model for expense categorization.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.core.database import Base


class Category(Base):
    """Category model for expense categorization."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False)  # System categories cannot be deleted
    color = Column(String, nullable=True)  # Hex color code for UI
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # None for system categories
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, name='{self.name}', is_system={self.is_system})>"
        )

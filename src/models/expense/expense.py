"""
Expense model for tracking user expenses.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class Expense(Base):
    """Expense model for tracking user expenses."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        String(20), default="pending", nullable=False
    )  # pending, approved, rejected
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(
        String(20), nullable=True
    )  # daily, weekly, monthly, yearly
    expense_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")

    def __repr__(self) -> str:
        return (
            f"<Expense(id={self.id}, amount={self.amount}, currency='{self.currency}')>"
        )

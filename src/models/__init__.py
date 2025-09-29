"""
Models package - import all models to ensure SQLAlchemy relationships work.
"""

from .category import Category
from .expense import Expense

# Import all models to ensure SQLAlchemy can resolve relationships
from .user import User

__all__ = ["User", "Category", "Expense"]

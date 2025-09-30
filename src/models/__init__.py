"""
Models package - import all models to ensure SQLAlchemy relationships work.
"""

from .category.category import Category
from .expense.expense import Expense
from .user.user import User

__all__ = ["User", "Category", "Expense"]

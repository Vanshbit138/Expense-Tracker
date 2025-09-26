"""
Async base repository with common CRUD operations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.logging_config import LoggerMixin

ModelType = TypeVar("ModelType")


class AsyncBaseRepository(Generic[ModelType], LoggerMixin):
    """Async base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, obj_in: ModelType) -> ModelType:
        """Create a new record."""
        try:
            self.db.add(obj_in)
            await self.db.commit()
            await self.db.refresh(obj_in)

            self.logger.info(
                "Record created",
                model=self.model.__name__,
                record_id=getattr(obj_in, "id", None),
            )

            return obj_in
        except Exception as e:
            await self.db.rollback()
            self.logger.error(
                "Failed to create record",
                model=self.model.__name__,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get record by ID."""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(
                "Failed to get record by ID",
                model=self.model.__name__,
                record_id=id,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_by_id_with_relations(
        self, id: Any, relations: List[str]
    ) -> Optional[ModelType]:
        """Get record by ID with specified relations loaded."""
        try:
            query = select(self.model).where(self.model.id == id)

            # Load specified relations
            for relation in relations:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(
                "Failed to get record by ID with relations",
                model=self.model.__name__,
                record_id=id,
                relations=relations,
                error=str(e),
                exc_info=True,
            )
            raise

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        try:
            query = select(self.model)

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.where(getattr(self.model, key) == value)

            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            self.logger.error(
                "Failed to get multiple records",
                model=self.model.__name__,
                skip=skip,
                limit=limit,
                filters=filters,
                error=str(e),
                exc_info=True,
            )
            raise

    async def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        try:
            # Get the record first
            record = await self.get_by_id(id)
            if not record:
                return None

            # Update fields
            for field, value in obj_in.items():
                if hasattr(record, field):
                    setattr(record, field, value)

            await self.db.commit()
            await self.db.refresh(record)

            self.logger.info("Record updated", model=self.model.__name__, record_id=id)

            return record
        except Exception as e:
            await self.db.rollback()
            self.logger.error(
                "Failed to update record",
                model=self.model.__name__,
                record_id=id,
                error=str(e),
                exc_info=True,
            )
            raise

    async def delete(self, id: Any) -> bool:
        """Delete a record."""
        try:
            result = await self.db.execute(
                delete(self.model).where(self.model.id == id)
            )
            await self.db.commit()

            deleted = result.rowcount > 0

            if deleted:
                self.logger.info(
                    "Record deleted", model=self.model.__name__, record_id=id
                )
            else:
                self.logger.warning(
                    "No record found to delete", model=self.model.__name__, record_id=id
                )

            return deleted
        except Exception as e:
            await self.db.rollback()
            self.logger.error(
                "Failed to delete record",
                model=self.model.__name__,
                record_id=id,
                error=str(e),
                exc_info=True,
            )
            raise

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        try:
            query = select(self.model)

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        query = query.where(getattr(self.model, key) == value)

            result = await self.db.execute(query)
            return len(result.scalars().all())
        except Exception as e:
            self.logger.error(
                "Failed to count records",
                model=self.model.__name__,
                filters=filters,
                error=str(e),
                exc_info=True,
            )
            raise

    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if record exists with given filters."""
        try:
            query = select(self.model)

            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            self.logger.error(
                "Failed to check record existence",
                model=self.model.__name__,
                filters=filters,
                error=str(e),
                exc_info=True,
            )
            raise

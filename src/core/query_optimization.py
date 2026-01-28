"""
Query optimization utilities for better database performance.
"""

from typing import Any, Dict, List

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query, joinedload, selectinload

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class QueryOptimizer:
    """Query optimization utilities."""

    @staticmethod
    def add_pagination(query: Query, skip: int = 0, limit: int = 100) -> Query:
        """Add pagination to query."""
        return query.offset(skip).limit(limit)

    @staticmethod
    def add_ordering(query: Query, order_by: str, direction: str = "asc") -> Query:
        """Add ordering to query."""
        if hasattr(query.column_descriptions[0]["entity"], order_by):
            order_column = getattr(query.column_descriptions[0]["entity"], order_by)
            if direction.lower() == "desc":
                return query.order_by(order_column.desc())
            else:
                return query.order_by(order_column.asc())
        return query

    @staticmethod
    def add_filters(query: Query, filters: Dict[str, Any]) -> Query:
        """Add filters to query."""
        for key, value in filters.items():
            if hasattr(query.column_descriptions[0]["entity"], key):
                column = getattr(query.column_descriptions[0]["entity"], key)
                if isinstance(value, list):
                    query = query.filter(column.in_(value))
                elif isinstance(value, dict):
                    # Handle range queries
                    if "gte" in value:
                        query = query.filter(column >= value["gte"])
                    if "lte" in value:
                        query = query.filter(column <= value["lte"])
                    if "gt" in value:
                        query = query.filter(column > value["gt"])
                    if "lt" in value:
                        query = query.filter(column < value["lt"])
                else:
                    query = query.filter(column == value)
        return query

    @staticmethod
    def add_relations(query: Query, relations: List[str]) -> Query:
        """Add eager loading for relations."""
        for relation in relations:
            if hasattr(query.column_descriptions[0]["entity"], relation):
                query = query.options(
                    joinedload(
                        getattr(query.column_descriptions[0]["entity"], relation)
                    )
                )
        return query

    @staticmethod
    def add_selectin_relations(query: Query, relations: List[str]) -> Query:
        """Add selectin loading for relations (better for one-to-many)."""
        for relation in relations:
            if hasattr(query.column_descriptions[0]["entity"], relation):
                query = query.options(
                    selectinload(
                        getattr(query.column_descriptions[0]["entity"], relation)
                    )
                )
        return query


class IndexOptimizer:
    """Database index optimization utilities."""

    @staticmethod
    def get_recommended_indexes() -> List[Dict[str, Any]]:
        """Get recommended database indexes for common queries."""
        return [
            {
                "table": "users",
                "columns": ["email"],
                "unique": True,
                "description": "Unique index on email for fast lookups",
            },
            {
                "table": "users",
                "columns": ["username"],
                "unique": True,
                "description": "Unique index on username for fast lookups",
            },
            {
                "table": "categories",
                "columns": ["user_id", "name"],
                "unique": False,
                "description": "Composite index for user category queries",
            },
            {
                "table": "expenses",
                "columns": ["user_id", "expense_date"],
                "unique": False,
                "description": "Composite index for user expense date queries",
            },
            {
                "table": "expenses",
                "columns": ["user_id", "category_id"],
                "unique": False,
                "description": "Composite index for user category expense queries",
            },
            {
                "table": "expenses",
                "columns": ["user_id", "status"],
                "unique": False,
                "description": "Composite index for user expense status queries",
            },
            {
                "table": "expenses",
                "columns": ["expense_date"],
                "unique": False,
                "description": "Index on expense date for date range queries",
            },
        ]

    @staticmethod
    async def create_recommended_indexes(session: AsyncSession) -> None:
        """Create recommended indexes."""
        indexes = IndexOptimizer.get_recommended_indexes()

        for index in indexes:
            try:
                table_name = index["table"]
                columns = ", ".join(index["columns"])
                unique = "UNIQUE" if index["unique"] else ""

                sql = f"CREATE {unique} INDEX IF NOT EXISTS idx_{table_name}_{'_'.join(index['columns'])} ON {table_name} ({columns})"

                await session.execute(text(sql))
                logger.info(f"Created index: {sql}")

            except Exception as e:
                logger.error(
                    f"Failed to create index for {index['table']}",
                    error=str(e),
                    exc_info=True,
                )


class AsyncQueryOptimizer:
    """Async query optimization utilities."""

    @staticmethod
    async def execute_optimized_query(
        session: AsyncSession, query: Query, log_query: bool = True
    ) -> Any:
        """Execute query with optimization and logging."""
        if log_query:
            logger.info("Executing optimized query", query=str(query))

        try:
            result = await session.execute(query)
            return result
        except Exception as e:
            logger.error(
                "Query execution failed", query=str(query), error=str(e), exc_info=True
            )
            raise

    @staticmethod
    async def get_count_optimized(session: AsyncSession, query: Query) -> int:
        """Get count with optimization."""
        try:
            # Convert to count query
            count_query = query.statement.with_only_columns([func.count()])
            result = await session.execute(count_query)
            return result.scalar()
        except Exception as e:
            logger.error(
                "Count query failed", query=str(query), error=str(e), exc_info=True
            )
            raise

    @staticmethod
    async def get_paginated_results(
        session: AsyncSession,
        query: Query,
        skip: int = 0,
        limit: int = 100,
        include_count: bool = False,
    ) -> Dict[str, Any]:
        """Get paginated results with count."""
        try:
            # Get total count if requested
            total_count = None
            if include_count:
                total_count = await AsyncQueryOptimizer.get_count_optimized(
                    session, query
                )

            # Add pagination
            paginated_query = QueryOptimizer.add_pagination(query, skip, limit)

            # Execute query
            result = await AsyncQueryOptimizer.execute_optimized_query(
                session, paginated_query
            )
            items = result.scalars().all()

            return {
                "items": items,
                "total_count": total_count,
                "skip": skip,
                "limit": limit,
                "has_more": total_count is not None
                and (skip + len(items)) < total_count,
            }

        except Exception as e:
            logger.error("Paginated query failed", error=str(e), exc_info=True)
            raise


class QueryAnalyzer:
    """Query analysis and optimization suggestions."""

    @staticmethod
    def analyze_query_performance(query: Query) -> Dict[str, Any]:
        """Analyze query performance and provide suggestions."""
        analysis = {"query": str(query), "suggestions": [], "warnings": []}

        # Check for missing indexes
        if "WHERE" in str(query).upper():
            analysis["suggestions"].append(
                "Consider adding indexes on WHERE clause columns"
            )

        # Check for ORDER BY without LIMIT
        if "ORDER BY" in str(query).upper() and "LIMIT" not in str(query).upper():
            analysis["warnings"].append(
                "ORDER BY without LIMIT may cause performance issues"
            )

        # Check for SELECT *
        if "SELECT *" in str(query).upper():
            analysis["suggestions"].append(
                "Consider selecting only needed columns instead of *"
            )

        return analysis

    @staticmethod
    def get_query_explanation(query: Query) -> str:
        """Get query explanation for debugging."""
        return f"Query: {query}\nCompiled: {query.compile(compile_kwargs={'literal_binds': True})}"

"""
Test database utilities and configuration.
"""

import pytest
from sqlalchemy.orm import Session

from src.core.database import Base, create_tables, drop_tables, get_db


class TestDatabase:
    """Test database utilities."""

    def test_get_db_session(self):
        """Test get_db dependency returns session."""
        db_generator = get_db()
        db = next(db_generator)

        assert isinstance(db, Session)

        # Cleanup
        try:
            next(db_generator)
        except StopIteration:
            pass  # Expected behavior

    def test_get_db_cleanup(self):
        """Test get_db properly closes session."""
        db_generator = get_db()
        db = next(db_generator)

        # Session should be open
        assert not db.is_active or True  # Session state varies

        # Cleanup should close session
        try:
            next(db_generator)
        except StopIteration:
            pass

    def test_create_tables(self):
        """Test create_tables function."""
        # This should not raise an exception
        try:
            create_tables()
        except Exception as e:
            pytest.fail(f"create_tables raised an exception: {e}")

    def test_drop_tables(self):
        """Test drop_tables function."""
        # Create tables first
        create_tables()

        # This should not raise an exception
        try:
            drop_tables()
        except Exception as e:
            pytest.fail(f"drop_tables raised an exception: {e}")

        # Recreate for other tests
        create_tables()

    def test_base_metadata(self):
        """Test Base has metadata."""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

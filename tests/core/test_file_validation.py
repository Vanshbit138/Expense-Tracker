"""
Tests for file validation module.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

from src.core.file_validation import FileValidator


class TestFileValidator:
    """Test cases for FileValidator class."""

    def test_file_validator_initialization(self):
        """Test FileValidator initialization."""
        validator = FileValidator()
        assert validator.magic is not None

    def test_validate_file_not_exists(self):
        """Test validation of non-existent file."""
        validator = FileValidator()
        is_valid, mime_type, error = validator.validate_file("/nonexistent/file.txt")

        assert is_valid is False
        assert mime_type == ""
        assert "does not exist" in error

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_file_success(self, mock_magic_class):
        """Test successful file validation."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "text/plain"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_file(tmp_path)

            assert is_valid is True
            assert mime_type == "text/plain"
            assert error == ""
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_file_size_exceeded(self, mock_magic_class):
        """Test file validation with size exceeded."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"test content" * 1000)
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "text/plain"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            # Set max size to 100 bytes (file is larger)
            is_valid, mime_type, error = validator.validate_file(tmp_path, max_size=100)

            assert is_valid is False
            assert "exceeds maximum" in error
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_file_with_allowed_categories(self, mock_magic_class):
        """Test file validation with allowed categories."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(b"fake image content")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "image/jpeg"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_file(
                tmp_path, allowed_categories=["image"]
            )

            assert is_valid is True
            assert mime_type == "image/jpeg"
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_file_invalid_type(self, mock_magic_class):
        """Test file validation with invalid file type."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
            tmp.write(b"executable content")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "application/x-executable"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_file(
                tmp_path, allowed_categories=["image"]
            )

            assert is_valid is False
            assert "not allowed" in error
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_image(self, mock_magic_class):
        """Test validate_image method."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(b"fake image")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "image/jpeg"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_image(tmp_path)

            assert is_valid is True
            assert mime_type == "image/jpeg"
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_document(self, mock_magic_class):
        """Test validate_document method."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"fake pdf")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "application/pdf"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_document(tmp_path)

            assert is_valid is True
            assert mime_type == "application/pdf"
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_spreadsheet(self, mock_magic_class):
        """Test validate_spreadsheet method."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(b"col1,col2\nval1,val2")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "text/csv"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_spreadsheet(tmp_path)

            assert is_valid is True
            assert mime_type == "text/csv"
        finally:
            os.unlink(tmp_path)

    @patch("src.core.file_validation.magic.Magic")
    def test_get_file_info(self, mock_magic_class):
        """Test get_file_info method."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.return_value = "text/plain"
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            info = validator.get_file_info(tmp_path)

            assert "file_path" in info
            assert "file_size" in info
            assert "mime_type" in info
            assert "file_name" in info
            assert "file_extension" in info
            assert info["mime_type"] == "text/plain"
        finally:
            os.unlink(tmp_path)

    def test_get_file_info_not_exists(self):
        """Test get_file_info with non-existent file."""
        validator = FileValidator()
        info = validator.get_file_info("/nonexistent/file.txt")

        assert "error" in info
        assert "does not exist" in info["error"]

    @patch("src.core.file_validation.magic.Magic")
    def test_validate_file_exception_handling(self, mock_magic_class):
        """Test exception handling in validate_file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            mock_magic = MagicMock()
            mock_magic.from_file.side_effect = Exception("Magic error")
            mock_magic_class.return_value = mock_magic

            validator = FileValidator()
            validator.magic = mock_magic

            is_valid, mime_type, error = validator.validate_file(tmp_path)

            assert is_valid is False
            assert "validation failed" in error.lower()
        finally:
            os.unlink(tmp_path)

    def test_file_validator_global_instance(self):
        """Test global file_validator instance."""
        from src.core.file_validation import file_validator

        assert file_validator is not None
        assert isinstance(file_validator, FileValidator)

"""
File validation utilities using python-magic.
"""

import os
from typing import List, Optional, Tuple

import magic

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class FileValidator:
    """File validation service using python-magic."""

    # Allowed file types and their MIME types
    ALLOWED_TYPES = {
        "image": [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
        ],
        "document": [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "text/csv",
        ],
        "spreadsheet": [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
        ],
    }

    # Maximum file sizes (in bytes)
    MAX_SIZES = {
        "image": 5 * 1024 * 1024,  # 5MB
        "document": 10 * 1024 * 1024,  # 10MB
        "spreadsheet": 10 * 1024 * 1024,  # 10MB
        "default": 5 * 1024 * 1024,  # 5MB
    }

    def __init__(self):
        self.magic = magic.Magic(mime=True)

    def validate_file(
        self,
        file_path: str,
        allowed_categories: List[str] = None,
        max_size: Optional[int] = None,
    ) -> Tuple[bool, str, str]:
        """
        Validate a file for type and size.

        Args:
            file_path: Path to the file to validate
            allowed_categories: List of allowed file categories
            max_size: Maximum file size in bytes

        Returns:
            Tuple of (is_valid, mime_type, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, "", "File does not exist"

            # Get file size
            file_size = os.path.getsize(file_path)

            # Get MIME type
            mime_type = self.magic.from_file(file_path)

            logger.info(
                "File validation started",
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
            )

            # Validate file size
            if max_size and file_size > max_size:
                return (
                    False,
                    mime_type,
                    f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
                )

            # If no categories specified, use default size check
            if not allowed_categories:
                default_max_size = self.MAX_SIZES["default"]
                if file_size > default_max_size:
                    return (
                        False,
                        mime_type,
                        f"File size exceeds maximum allowed size ({default_max_size} bytes)",
                    )
                return True, mime_type, ""

            # Validate file type against allowed categories
            allowed_mime_types = []
            for category in allowed_categories:
                if category in self.ALLOWED_TYPES:
                    allowed_mime_types.extend(self.ALLOWED_TYPES[category])

            if mime_type not in allowed_mime_types:
                return (
                    False,
                    mime_type,
                    f"File type '{mime_type}' is not allowed. Allowed types: {allowed_mime_types}",
                )

            # Validate file size for specific category
            category_max_size = self.MAX_SIZES.get(
                allowed_categories[0], self.MAX_SIZES["default"]
            )
            if file_size > category_max_size:
                return (
                    False,
                    mime_type,
                    f"File size ({file_size} bytes) exceeds maximum allowed size for {allowed_categories[0]} ({category_max_size} bytes)",
                )

            logger.info(
                "File validation successful",
                file_path=file_path,
                mime_type=mime_type,
                file_size=file_size,
            )

            return True, mime_type, ""

        except Exception as e:
            logger.error(
                "File validation failed",
                file_path=file_path,
                error=str(e),
                exc_info=True,
            )
            return False, "", f"File validation failed: {str(e)}"

    def validate_image(
        self, file_path: str, max_size: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """Validate an image file."""
        return self.validate_file(file_path, ["image"], max_size)

    def validate_document(
        self, file_path: str, max_size: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """Validate a document file."""
        return self.validate_file(file_path, ["document"], max_size)

    def validate_spreadsheet(
        self, file_path: str, max_size: Optional[int] = None
    ) -> Tuple[bool, str, str]:
        """Validate a spreadsheet file."""
        return self.validate_file(file_path, ["spreadsheet"], max_size)

    def get_file_info(self, file_path: str) -> dict:
        """Get comprehensive file information."""
        try:
            if not os.path.exists(file_path):
                return {"error": "File does not exist"}

            file_size = os.path.getsize(file_path)
            mime_type = self.magic.from_file(file_path)

            return {
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mime_type,
                "file_name": os.path.basename(file_path),
                "file_extension": os.path.splitext(file_path)[1].lower(),
            }

        except Exception as e:
            logger.error(
                "Failed to get file info",
                file_path=file_path,
                error=str(e),
                exc_info=True,
            )
            return {"error": str(e)}


# Global file validator instance
file_validator = FileValidator()

#!/usr/bin/env python3
"""
Setup script for Expense Tracker API.
"""
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="expense-tracker",
    version="1.0.0",
    author="Expense Tracker Team",
    author_email="team@expensetracker.com",
    description="A RESTful Expense Tracker API built with FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/expense-tracker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.12.0",
            "httpx>=0.25.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "expense-tracker=src.api.main:app",
        ],
    },
)

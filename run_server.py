#!/usr/bin/env python3
"""
Entry point for running the Expense Tracker API server.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )

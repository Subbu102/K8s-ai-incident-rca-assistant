#!/usr/bin/env python
"""
Development server with hot reload.
"""

import os
import sys
import logging

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True,
        log_level=os.getenv("API_LOG_LEVEL", "info")
    )

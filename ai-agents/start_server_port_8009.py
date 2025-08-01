#!/usr/bin/env python3

# Temporary server starter on port 8009 to test fixes
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from main import app

if __name__ == "__main__":
    print("Starting InstaBids server on port 8009 with latest fixes...")
    uvicorn.run(app, host="0.0.0.0", port=8009)
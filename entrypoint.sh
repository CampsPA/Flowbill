#!/bin/bash

# This file 
# 1- Runs Alembic upgread head
# 2- Starts Uvicorn

# Make the script  exit immediately if any command fails
set -e

# Set up logic
 alembic upgrade head

# Clear stale .pyc files and __pycache__ dirs so Python always loads fresh source
find /app -name "*.pyc" -delete && find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

 # Run the main container command -> this tiggers CMD to run uvicorn
exec "$@"


# Important detail about exec  — it doesn't just run the command,
# it replaces the current shell process with the new command. This means Uvicorn becomes 
# PID 1 directly, which provides the graceful shutdown benefit from the CMD exec.
# SIGTERM goes straight to Uvicorn.

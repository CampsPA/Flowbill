#!/bin/bash

# This file 
# 1- Runs Alembic upgread head
# 2- Starts Uvicorn

# Make the script  exit immediately if any command fails
set -e

# Set up logic
 alembic upgrade head

 # Run the main container command -> this tiggers CMD to run uvicorn
exec "$@"


# Important detail about exec  — it doesn't just run the command,
# it replaces the current shell process with the new command. This means Uvicorn becomes 
# PID 1 directly, which provides the graceful shutdown benefit from the CMD exec.
# SIGTERM goes straight to Uvicorn.

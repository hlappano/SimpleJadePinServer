#!/bin/bash

LOG_FILE="/app/npm_run.log"

# Build the frontend
cd /app/web

# Start static server for frontend
PORT=5000 HOST=0.0.0.0 node build/index.js > ${LOG_FILE} 2>&1 &

# Start the backend server
echo "Starting backend server..."
cd /app/server
python3 SimpleJadePinServer.py "$@"
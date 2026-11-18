#!/bin/bash

LOG_FILE="/app/npm_run.log"

# Build the frontend
cd /app/web
# Run build
npm run build

# Start static server for frontend
npm run preview -- --host 0.0.0.0 --port 5000 > ${LOG_FILE} &

# Start the backend server
echo "Starting backend server..."
cd /app/server
python3 SimpleJadePinServer.py "$@"
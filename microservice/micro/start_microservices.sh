#!/bin/bash

set -e

# Start the data, analytics, and gateway services in a single tmux session for local testing.
tmux new-session -d -s microservices "python data_service.py"

tmux split-window -h -t microservices "DATA_SERVICE_URL=http://localhost:5001 python analytics_service.py"

tmux split-window -v -t microservices "DATA_SERVICE_URL=http://localhost:5001 ANALYTICS_SERVICE_URL=http://localhost:5002 python api_gateway.py"

tmux attach-session -t microservices

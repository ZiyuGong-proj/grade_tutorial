#!/bin/bash

tmux new-session -d -s microservices "python user_service.py"

tmux split-window -h -t microservices "python order_service.py"

tmux split-window -v -t microservices "python api_gateway.py"

tmux attach-session -t microservices

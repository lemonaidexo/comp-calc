#!/bin/bash

echo "Stopping current process..."
pkill -f "docker compose up"
sleep 2

echo "Taking down containers..."
docker compose down
sleep 2

echo "Rebuilding and starting containers..."
docker compose up --build
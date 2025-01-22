#!/bin/bash
set -e

# Git Pull
echo "Pulling latest changes..."
git pull

# Install dependencies
echo "Installing dependencies..."
yarn install

# Build the application
echo "Building the application..."
yarn build

# Restart PM2 process
echo "Restarting PM2 process..."
pm2 delete frontend || true
pm2 start yarn --name frontend -- start

echo "Deployment completed successfully."

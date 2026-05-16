#!/bin/bash

set -e

ROOT_DIR="$(pwd)"

echo "Updating repository..."
git -C "$ROOT_DIR" pull

echo "Building home..."
cd "$ROOT_DIR/home"
zola build

echo "Building blog..."
cd "$ROOT_DIR/blog"
zola build

echo "Install the new deps..."
cd "$ROOT_DIR"
pip install -r requirements.txt --break-system-packages

echo "Restarting webserver..."
sudo systemctl restart webserver

echo "Done."

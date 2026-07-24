#!/bin/bash
set -e

echo "=== Post-merge setup ==="

echo "--- Running Django migrations ---"
cd back && python3 manage.py migrate --noinput

echo "--- Installing Node dependencies ---"
cd ../Front && npm install --legacy-peer-deps --prefer-offline

echo "=== Done ==="

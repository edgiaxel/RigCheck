#!/usr/bin/env bash
set -e

echo ">>> [RigCheck] Installing frontend dependencies..."
npm --prefix frontend install

echo ">>> [RigCheck] Building production static bundle..."
npm --prefix frontend run build

echo ">>> [RigCheck] Production build complete in frontend/dist."

#!/usr/bin/env bash
set -euo pipefail
uv venv
uv sync --all-extras --dev
cp -n .env.example .env || true

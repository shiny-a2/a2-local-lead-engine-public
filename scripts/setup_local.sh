#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp -n .env.example .env
python -m app.cli.main doctor


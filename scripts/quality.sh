#!/bin/sh
set -eu
export UV_CACHE_DIR="${UV_CACHE_DIR:-.cache/uv}"
uv run --frozen ruff check backend scripts
uv run --frozen ruff format --check backend scripts
uv run --frozen mypy
uv run --frozen pytest

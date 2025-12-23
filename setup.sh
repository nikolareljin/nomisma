#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/nikolareljin/nomisma.git}"
DEFAULT_INSTALL_DIR="${1:-nomisma}"

printf "Install path [%s]: " "$DEFAULT_INSTALL_DIR"
read -r INSTALL_DIR_INPUT
INSTALL_DIR="${INSTALL_DIR_INPUT:-$DEFAULT_INSTALL_DIR}"

open_url() {
    local url="$1"
    if command -v open >/dev/null 2>&1; then
        open "$url"
        return 0
    fi
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$url"
        return 0
    fi
    if command -v sensible-browser >/dev/null 2>&1; then
        sensible-browser "$url"
        return 0
    fi
    echo "Open this URL in your browser: $url"
}

require_cmd() {
    local cmd="$1"
    local url="$2"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Missing dependency: $cmd"
        open_url "$url"
        exit 1
    fi
}

require_cmd git "https://git-scm.com/downloads"

if ! command -v docker >/dev/null 2>&1; then
    echo "Missing dependency: docker"
    open_url "https://docs.docker.com/get-docker/"
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    : # Docker Compose plugin is available.
elif command -v docker-compose >/dev/null 2>&1; then
    : # Legacy docker-compose binary is available.
else
    echo "Missing dependency: docker compose"
    open_url "https://docs.docker.com/compose/install/"
    exit 1
fi

if [ -e "$INSTALL_DIR" ]; then
    echo "Install directory already exists: $INSTALL_DIR"
    echo "Remove it or pick a different path."
    exit 1
fi

echo "Cloning $REPO_URL into $INSTALL_DIR"
git clone "$REPO_URL" "$INSTALL_DIR"

cd "$INSTALL_DIR"

if [ -x "./update" ]; then
    ./update
else
    git submodule update --init --recursive
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

echo "Setup complete."
echo "Next steps:"
echo "  cd $INSTALL_DIR"
echo "  ./start"

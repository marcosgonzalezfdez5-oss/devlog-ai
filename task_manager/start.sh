#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

initialize_app() {
    local DIR="$1"
    local VENV_PATH="$DIR/venv"
    local PYTHON_EXE="$VENV_PATH/bin/python"

    if [[ ! -f "$PYTHON_EXE" ]]; then
        echo "Creating virtual environment in $DIR..."

        # Use Python 3.13 if available, otherwise fallback to python3
        if command -v python3.13 >/dev/null 2>&1; then
            python3.13 -m venv "$VENV_PATH"
        else
            python3 -m venv "$VENV_PATH"
        fi

        "$PYTHON_EXE" -m pip install --upgrade pip
        "$PYTHON_EXE" -m pip install -r "$DIR/requirements.txt"
    fi

    local ENV_FILE="$DIR/.env"
    local ENV_EXAMPLE="$DIR/.env.example"

    if [[ ! -f "$ENV_FILE" && -f "$ENV_EXAMPLE" ]]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo "WARNING: Created $ENV_FILE from .env.example."
        echo "Fill in the real values before using the application."
    fi
}

start_in_terminal() {
    local TITLE="$1"
    local CMD="$2"

    if command -v gnome-terminal >/dev/null 2>&1; then
        gnome-terminal --title="$TITLE" -- bash -c "$CMD; exec bash"
    elif command -v konsole >/dev/null 2>&1; then
        konsole --hold -e bash -c "$CMD"
    elif command -v xfce4-terminal >/dev/null 2>&1; then
        xfce4-terminal --hold -e "bash -c '$CMD'"
    elif command -v xterm >/dev/null 2>&1; then
        xterm -hold -e "$CMD" &
    else
        echo "No supported terminal emulator found."
        echo "Starting $TITLE in the background..."
        bash -c "$CMD" &
    fi
}

initialize_app "$BACKEND_DIR"
initialize_app "$FRONTEND_DIR"

BACKEND_PYTHON="$BACKEND_DIR/venv/bin/python"
FRONTEND_PYTHON="$FRONTEND_DIR/venv/bin/python"

echo "Starting backend (FastAPI) on http://localhost:8000..."

start_in_terminal \
    "FastAPI Backend" \
    "cd \"$BACKEND_DIR\" && \"$BACKEND_PYTHON\" -m uvicorn app.main:app --reload --port 8000"

sleep 2

echo "Starting frontend (Streamlit) on http://localhost:8501..."

start_in_terminal \
    "Streamlit Frontend" \
    "cd \"$FRONTEND_DIR\" && \"$FRONTEND_PYTHON\" -m streamlit run app.py"

echo
echo "Both applications are starting in separate terminal windows."
echo "Close those windows to stop the applications."
#!/bin/zsh
set -e

export MPLCONFIGDIR="${TMPDIR:-/tmp}/mediapipe_showcase_mpl"

PYTHON="/Users/zihan/.pyenv/versions/3.12.7/bin/python3"
SCRIPT="/Users/zihan/Downloads/mediapipe_showcase.py"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python not found: $PYTHON"
  exit 1
fi

if [[ ! -f "$SCRIPT" ]]; then
  echo "Script not found: $SCRIPT"
  exit 1
fi

exec "$PYTHON" "$SCRIPT" "$@"

#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1
python -m streamlit run src/ui/app.py --server.address localhost "$@"

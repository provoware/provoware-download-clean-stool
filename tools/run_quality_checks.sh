#!/bin/bash
# Run a basic quality check on Python sources.

echo "[QUALITY] Running Python compilation checks..."
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/.. && pwd )"

python3 -m compileall -q "$ROOT_DIR/app" "$ROOT_DIR/core"
if [ $? -ne 0 ]; then
  echo "[QUALITY] Compilation failed"
  exit 1
fi
echo "[QUALITY] Checks passed"
exit 0

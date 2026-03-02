#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <input.alg> [output_binary]"
  exit 1
fi

INPUT="$1"

if [[ ! -f "$INPUT" ]]; then
  echo "Error: input file '$INPUT' not found"
  exit 1
fi

BASENAME="$(basename "$INPUT")"
NAME="${BASENAME%.*}"

C_OUT="generated/${NAME}.c"
BIN_OUT="generated/${2:-$NAME}"

mkdir -p generated

python3 compile.py "$INPUT" -o "$C_OUT"
gcc "$C_OUT" -o "$BIN_OUT"

printf "Built executable: %s\n" "$BIN_OUT"
printf "Running...\n"
"./$BIN_OUT"

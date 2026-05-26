#!/usr/bin/env bash
set -euo pipefail

printf "Agenda Cultural GC — local harness check\n"
printf "=======================================\n"

if command -v node >/dev/null 2>&1; then
  printf "Node: "
  node --version
else
  printf "Node: not found\n"
fi

if command -v npm >/dev/null 2>&1; then
  printf "npm: "
  npm --version
else
  printf "npm: not found\n"
fi

if command -v python >/dev/null 2>&1; then
  printf "Python: "
  python --version
else
  printf "Python: not found\n"
fi

printf "\nExisting commands documented in TESTING.md.\n"
printf "This script does not install dependencies, touch secrets, run production, or modify scrapers.\n"

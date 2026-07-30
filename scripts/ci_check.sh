#!/usr/bin/env bash
#
# ci_check.sh — the single entry point CI uses, and the same command you run
# locally before pushing.  Every stage is guarded so the pipeline is green from
# day one and becomes progressively more meaningful as the repo fills in.
#
#   ./scripts/ci_check.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

pass=0
skip=0

hdr() { printf '\n\033[1m── %s\033[0m\n' "$1"; }
ok()  { printf '   \033[32mPASS\033[0m %s\n' "$1"; pass=$((pass + 1)); }
sk()  { printf '   \033[33mSKIP\033[0m %s\n' "$1"; skip=$((skip + 1)); }

# ─── 1. Verilator lint on all design sources ─────────────────────────────────
hdr "Verilator lint"
mapfile -t rtl_files < <(find rtl -name '*.sv' -o -name '*.v' 2>/dev/null | sort)
if [ ${#rtl_files[@]} -eq 0 ]; then
  sk "no RTL sources in rtl/ yet"
else
  for f in "${rtl_files[@]}"; do
    # -Wall is deliberate: WIDTH and UNUSED warnings are exactly the class of
    # bug that survives simulation and dies in synthesis.
    verilator --lint-only -Wall -Irtl "$f"
    ok "$f"
  done
fi

# ─── 2. Python golden-model tests ────────────────────────────────────────────
hdr "Golden-model tests (pytest)"
if compgen -G "tb/python/test_*.py" > /dev/null || compgen -G "tb/python/tests/test_*.py" > /dev/null; then
  python -m pytest tb/python -q
  ok "tb/python"
else
  sk "no golden-model tests yet"
fi

# ─── 3. cocotb regression ────────────────────────────────────────────────────
hdr "cocotb regression (Verilator)"
if [ -f tb/tests/Makefile ]; then
  make -C tb/tests sim
  ok "tb/tests"
else
  sk "no tb/tests/Makefile yet"
fi

printf '\n\033[1mSummary:\033[0m %d passed, %d skipped\n' "$pass" "$skip"

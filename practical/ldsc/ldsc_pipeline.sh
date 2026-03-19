#!/usr/bin/env bash
set -euo pipefail

# Student-facing LDSC practical.
# Assumes the instructor has already created the prepared inputs with:
#   Rscript practical/ldsc/prepare_ldsc_data.R [--force]
#
# `set -euo pipefail` makes the script safer for teaching and reproducibility:
# - `-e` stops at the first failing command
# - `-u` fails on unset variables instead of silently using empty strings
# - `pipefail` makes a pipeline fail if any command inside it fails

# Resolve the main directories used throughout the practical.
# Students should not need to edit these in the common case.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HOST_UNAME_S="$(uname -s)"
LDSC_DIR="${LDSC_DIR:-${SCRIPT_DIR}/ldsc}"
LDSC_ENV_DIR="${LDSC_ENV_DIR:-${SCRIPT_DIR}/.venv/ldsc}"
COURSE_DIR="${SCRIPT_DIR}/data/course"
REF_DIR="${SCRIPT_DIR}/data/ref"
RESULTS_DIR="${SCRIPT_DIR}/data/results"

# These are the course-ready summary-statistics files created by
# `prepare_ldsc_data.R`. They already have a standard LDSC-friendly schema.
INTELLIGENCE_INPUT="${COURSE_DIR}/intelligence_ctg.tsv.gz"
P_FACTOR_INPUT="${COURSE_DIR}/p_factor.tsv.gz"

# Test whether a candidate Python command exists and is new enough for the
# local CBIIT/ldsc install. The course workflow expects Python 3.9+.
python_cmd_is_usable() {
  "$@" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 9) else 1)
PY
}

# If a Python command works, store it as the interpreter this script will use.
set_python_cmd_if_usable() {
  if python_cmd_is_usable "$@"; then
    PYTHON_CMD=("$@")
    return 0
  fi

  return 1
}

# Find a working Python interpreter.
# We prefer the course-local virtual environment, but also fall back to common
# system locations so the script works smoothly in Git Bash on Windows.
detect_python_cmd() {
  if [[ -n "${LDSC_PYTHON:-}" ]] && set_python_cmd_if_usable "${LDSC_PYTHON}"; then
    return
  fi

  if [[ -f "${LDSC_ENV_DIR}/Scripts/python.exe" ]] && set_python_cmd_if_usable "${LDSC_ENV_DIR}/Scripts/python.exe"; then
    return
  fi

  if [[ -x "${LDSC_ENV_DIR}/bin/python" ]] && set_python_cmd_if_usable "${LDSC_ENV_DIR}/bin/python"; then
    return
  fi

  if [[ -f "${LDSC_ENV_DIR}/python.exe" ]] && set_python_cmd_if_usable "${LDSC_ENV_DIR}/python.exe"; then
    return
  fi

  if command -v python3 >/dev/null 2>&1 && set_python_cmd_if_usable python3; then
    return
  fi

  if command -v py >/dev/null 2>&1 && set_python_cmd_if_usable py -3; then
    return
  fi

  local -a candidates
  shopt -s nullglob
  candidates=(
    /c/Users/*/AppData/Local/Programs/Python/Python*/python.exe
    "/c/Program Files"/Python*/python.exe
    "/c/Program Files (x86)"/Python*/python.exe
  )
  shopt -u nullglob

  local candidate
  for candidate in "${candidates[@]}"; do
    if set_python_cmd_if_usable "${candidate}"; then
      return
    fi
  done

  if command -v python >/dev/null 2>&1 && set_python_cmd_if_usable python; then
    return
  fi

  echo "Could not find a working Python 3.9+ interpreter for LDSC." >&2
  echo "Run: bash practical/ldsc/install_ldsc.sh" >&2
  exit 1
}

# LDSC is a Python program, and native Windows / Git Bash paths can otherwise be
# interpreted inconsistently. We convert paths to a Python-friendly form on
# Windows so that LDSC sees `D:/...` paths instead of shell-specific `/d/...`
# paths. This matters especially for comma-separated arguments like `--rg`.
path_for_python() {
  local path="$1"
  if [[ "${HOST_UNAME_S}" == MINGW* || "${HOST_UNAME_S}" == MSYS* || "${HOST_UNAME_S}" == CYGWIN* ]]; then
    local converted
    converted="$(cygpath -am "${path}")"
    if [[ "${path}" == */ ]]; then
      converted="${converted}/"
    fi
    printf '%s\n' "${converted}"
  else
    printf '%s\n' "${path}"
  fi
}

PYTHON_CMD=()
detect_python_cmd

# Check that LDSC itself is installed where we expect it. The installer script
# places `munge_sumstats.py` and `ldsc.py` in `practical/ldsc/ldsc`.
if [[ ! -f "${LDSC_DIR}/munge_sumstats.py" || ! -f "${LDSC_DIR}/ldsc.py" ]]; then
  echo "Could not find LDSC in ${LDSC_DIR}" >&2
  echo "Run: bash practical/ldsc/install_ldsc.sh" >&2
  echo "Or set LDSC_DIR to the directory containing munge_sumstats.py and ldsc.py" >&2
  exit 1
fi

# Check that the prepared course data and the HapMap3 SNP list exist.
# The HapMap3 list is used with `--merge-alleles` so LDSC keeps a consistent,
# high-quality SNP set across traits.
for required_file in \
  "${INTELLIGENCE_INPUT}" \
  "${P_FACTOR_INPUT}" \
  "${REF_DIR}/w_hm3.snplist"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "Missing required input: ${required_file}" >&2
    echo "Run: Rscript practical/ldsc/prepare_ldsc_data.R --force" >&2
    exit 1
  fi
done

mkdir -p "${RESULTS_DIR}"

# Convert all file and prefix paths into the form Python/LDSC should receive.
# `--ref-ld-chr` and `--w-ld-chr` point to chromosome-split prefixes rather than
# single files: LDSC automatically expands them to chromosomes 1-22.
INTELLIGENCE_INPUT_PY="$(path_for_python "${INTELLIGENCE_INPUT}")"
P_FACTOR_INPUT_PY="$(path_for_python "${P_FACTOR_INPUT}")"
MERGE_ALLELES_PY="$(path_for_python "${REF_DIR}/w_hm3.snplist")"
REF_LD_CHR_PY="$(path_for_python "${REF_DIR}/eur_w_ld_chr/")"
W_LD_CHR_PY="$(path_for_python "${REF_DIR}/weights_hm3_no_hla/weights.hm3_noMHC.")"
INTELLIGENCE_PREFIX_PY="$(path_for_python "${RESULTS_DIR}/intelligence_ctg")"
P_FACTOR_PREFIX_PY="$(path_for_python "${RESULTS_DIR}/p_factor")"
INTELLIGENCE_H2_OUT_PY="$(path_for_python "${RESULTS_DIR}/intelligence_h2")"
P_FACTOR_H2_OUT_PY="$(path_for_python "${RESULTS_DIR}/p_factor_h2")"
RG_OUT_PY="$(path_for_python "${RESULTS_DIR}/intelligence_p_factor_rg")"
RG_INPUT_PY="${INTELLIGENCE_PREFIX_PY}.sumstats.gz,${P_FACTOR_PREFIX_PY}.sumstats.gz"

# Step 1: Munge the prepared course files into LDSC's own `.sumstats.gz` format.
# `--merge-alleles` keeps only the SNPs in the HapMap3 merge list and helps make
# the downstream heritability and genetic-correlation runs comparable.
"${PYTHON_CMD[@]}" "${LDSC_DIR}/munge_sumstats.py" \
  --sumstats "${INTELLIGENCE_INPUT_PY}" \
  --out "${INTELLIGENCE_PREFIX_PY}" \
  --merge-alleles "${MERGE_ALLELES_PY}"

"${PYTHON_CMD[@]}" "${LDSC_DIR}/munge_sumstats.py" \
  --sumstats "${P_FACTOR_INPUT_PY}" \
  --out "${P_FACTOR_PREFIX_PY}" \
  --merge-alleles "${MERGE_ALLELES_PY}"

# Step 2: Run single-trait LDSC (`--h2`) for each munged file.
# We use the munged `.sumstats.gz` outputs here, not the course `.tsv.gz` files,
# because LDSC expects its own post-munge format for heritability regression.
"${PYTHON_CMD[@]}" "${LDSC_DIR}/ldsc.py" \
  --h2 "${INTELLIGENCE_PREFIX_PY}.sumstats.gz" \
  --ref-ld-chr "${REF_LD_CHR_PY}" \
  --w-ld-chr "${W_LD_CHR_PY}" \
  --out "${INTELLIGENCE_H2_OUT_PY}"

"${PYTHON_CMD[@]}" "${LDSC_DIR}/ldsc.py" \
  --h2 "${P_FACTOR_PREFIX_PY}.sumstats.gz" \
  --ref-ld-chr "${REF_LD_CHR_PY}" \
  --w-ld-chr "${W_LD_CHR_PY}" \
  --out "${P_FACTOR_H2_OUT_PY}"

# Step 3: Run cross-trait LDSC (`--rg`) on the two munged files.
# The comma-separated `--rg` argument is why explicit path normalization matters
# on Windows/Git Bash: LDSC must receive two valid Python-readable file paths.
"${PYTHON_CMD[@]}" "${LDSC_DIR}/ldsc.py" \
  --rg "${RG_INPUT_PY}" \
  --ref-ld-chr "${REF_LD_CHR_PY}" \
  --w-ld-chr "${W_LD_CHR_PY}" \
  --out "${RG_OUT_PY}"

# Print a compact summary so students do not need to open the full log files to
# find the key quantities from the practical.
grep -E "Total Observed scale h2|Intercept|Ratio" "${RESULTS_DIR}/intelligence_h2.log"
grep -E "Total Observed scale h2|Intercept|Ratio" "${RESULTS_DIR}/p_factor_h2.log"
grep -E "Genetic Correlation|Intercept|P:" "${RESULTS_DIR}/intelligence_p_factor_rg.log"

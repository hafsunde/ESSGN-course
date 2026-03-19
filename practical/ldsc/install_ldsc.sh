#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LDSC_DIR="${LDSC_DIR:-${SCRIPT_DIR}/ldsc}"
LDSC_ENV_DIR="${LDSC_ENV_DIR:-${SCRIPT_DIR}/.venv/ldsc}"
LDSC_REPO_URL="${LDSC_REPO_URL:-https://github.com/CBIIT/ldsc.git}"
LDSC_BRANCH="${LDSC_BRANCH:-ldsc39}"
HOST_UNAME_S="$(uname -s)"

require_cmd() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Could not find ${cmd} on PATH. ${hint}" >&2
    exit 1
  fi
}

looks_like_cbiit_ldsc() {
  [[ -f "$1/environment3.yml" ]]
}

backup_non_course_checkout() {
  local backup_path
  backup_path="${LDSC_DIR}.backup.$(date +%Y%m%d%H%M%S)"
  echo "Existing checkout in ${LDSC_DIR} does not match the course installer target." >&2
  echo "Moving it to ${backup_path}" >&2
  mv "${LDSC_DIR}" "${backup_path}"
}

python_cmd_is_usable() {
  "$@" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 9) else 1)
PY
}

set_python_cmd_if_usable() {
  if python_cmd_is_usable "$@"; then
    PYTHON_CMD=("$@")
    return 0
  fi

  return 1
}

detect_python_cmd() {
  if command -v python3 >/dev/null 2>&1 && set_python_cmd_if_usable python3; then
    return
  fi

  if command -v py >/dev/null 2>&1 && set_python_cmd_if_usable py -3; then
    return
  fi

  if [[ "${HOST_UNAME_S}" == MINGW* || "${HOST_UNAME_S}" == MSYS* || "${HOST_UNAME_S}" == CYGWIN* ]]; then
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
  fi

  if command -v python >/dev/null 2>&1 && set_python_cmd_if_usable python; then
    return
  fi

  echo "Could not find a working Python 3.9+ interpreter." >&2
  echo "Install Python 3.9+ and ensure it is available as python3, py -3, or python." >&2
  echo "On Windows, if Python is installed but hidden from Git Bash, add it to PATH or install Python for all users." >&2
  exit 1
}

find_venv_python() {
  if [[ -f "${LDSC_ENV_DIR}/Scripts/python.exe" ]]; then
    VENV_PYTHON="${LDSC_ENV_DIR}/Scripts/python.exe"
    return
  fi

  if [[ -f "${LDSC_ENV_DIR}/bin/python" ]]; then
    VENV_PYTHON="${LDSC_ENV_DIR}/bin/python"
    return
  fi

  echo "Could not find the virtual environment Python executable in ${LDSC_ENV_DIR}" >&2
  exit 1
}

require_cmd git "Install git first, then rerun this script."
detect_python_cmd

if [[ "${HOST_UNAME_S}" == MINGW* || "${HOST_UNAME_S}" == MSYS* || "${HOST_UNAME_S}" == CYGWIN* ]]; then
  echo "Installing for native Windows/Git Bash using the local virtual environment."
  echo "WSL remains optional, but is not required by this installer."
fi

mkdir -p "${SCRIPT_DIR}"

if [[ -d "${LDSC_DIR}" ]]; then
  if looks_like_cbiit_ldsc "${LDSC_DIR}"; then
    echo "Reusing existing CBIIT LDSC checkout in ${LDSC_DIR}"
    if [[ -d "${LDSC_DIR}/.git" ]]; then
      git -C "${LDSC_DIR}" fetch origin "${LDSC_BRANCH}" --depth 1
      git -C "${LDSC_DIR}" checkout "${LDSC_BRANCH}"
      git -C "${LDSC_DIR}" pull --ff-only origin "${LDSC_BRANCH}"
    fi
  else
    backup_non_course_checkout
  fi
fi

if [[ ! -d "${LDSC_DIR}" ]]; then
  echo "Cloning CBIIT LDSC (${LDSC_BRANCH}) into ${LDSC_DIR}"
  git clone --branch "${LDSC_BRANCH}" --single-branch "${LDSC_REPO_URL}" "${LDSC_DIR}"
fi

if [[ ! -f "${LDSC_DIR}/ldsc.py" || ! -f "${LDSC_DIR}/munge_sumstats.py" ]]; then
  echo "The cloned repository does not contain the expected LDSC CLI files." >&2
  exit 1
fi

if [[ ! -d "${LDSC_ENV_DIR}" ]]; then
  echo "Creating local virtual environment in ${LDSC_ENV_DIR}"
  if ! "${PYTHON_CMD[@]}" -m venv "${LDSC_ENV_DIR}"; then
    echo "Failed to create the virtual environment." >&2
    echo "On Linux you may need: sudo apt install python3-venv" >&2
    exit 1
  fi
else
  echo "Reusing existing virtual environment in ${LDSC_ENV_DIR}"
fi

find_venv_python

echo "Installing LDSC Python dependencies"
"${VENV_PYTHON}" -m pip install --upgrade pip setuptools wheel
"${VENV_PYTHON}" -m pip install bitarray numpy pandas scipy nose

echo "Verifying LDSC installation"
"${VENV_PYTHON}" "${LDSC_DIR}/ldsc.py" -h >/dev/null
"${VENV_PYTHON}" "${LDSC_DIR}/munge_sumstats.py" -h >/dev/null

cat <<EOF

LDSC is installed locally for this practical.

Repository:
  ${LDSC_DIR}

Branch:
  ${LDSC_BRANCH}

Environment:
  ${LDSC_ENV_DIR}

Notes:
  This installer skips annotation-only dependencies such as pybedtools.
  That is fine for the course workflow using munge_sumstats.py, ldsc.py --h2, and ldsc.py --rg.

Next step:
  bash practical/ldsc/ldsc_pipeline.sh
EOF

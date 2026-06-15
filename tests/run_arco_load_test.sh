#!/usr/bin/env bash
#
# run_load_test.sh
#
# Launches `arco_load_test.py` concurrently as several different Linux users
# (via `sudo -u`), to simulate ~N students hitting the ARCO Zarr store and the
# Slurm/Dask cluster at the same time.
#
# Each user gets:
#   - its own SLURMCluster (created inside arco_load_test.py)
#   - its own worker-job log directory
#   - its own results file (written under that user's $HOME, so no
#     permission issues with sudo)
#
# After all runs finish, this script concatenates the per-user results files
# into one combined JSON-lines file for analysis.
#
# -----------------------------------------------------------------------------
# USAGE
#   ./run_load_test.sh [options]
#
# OPTIONS (all optional, override via env vars or flags below)
#   -u "user1 user2 ..."   Space-separated list of usernames to run as.
#                          Default: student01..student20
#   -s /path/to/script     Path to arco_load_test.py (must be readable by all
#                          users). Default: ./arco_load_test.py
#   -p python_bin          Python executable to use (e.g. a shared conda env
#                          interpreter). Default: python3
#   -j N                   --jobs value passed to arco_load_test.py (Dask
#                          worker jobs per user). Default: 2
#   -d                     Also pass --with-diff (extra compute load).
#   -o /path/to/combined.jsonl
#                          Where to write the combined results file on this
#                          host. Default: ./combined_results.jsonl
#   -w SECONDS             Stagger: sleep this many seconds between launching
#                          each user's job, instead of launching all at once.
#                          Default: 0 (all at once -> max concurrency).
#
# EXAMPLE
#   ./run_load_test.sh -u "student01 student02 student03" \
#                       -s /home/shared/arco_load_test.py \
#                       -p /home/shared/envs/dask-env/bin/python \
#                       -j 2 -d -o /home/admin/load_test_$(date +%Y%m%d_%H%M%S).jsonl
#
# NOTES
#   - Run this script itself as root (or a user with sudo rights to switch to
#     each target user) since it relies on `sudo -u`.
#   - `arco_load_test.py` must be readable (and its parent dirs traversable)
#     by every target user.
#   - Each user's $HOME must exist and be writable by that user, since results
#     and Dask worker logs are written there.
# -----------------------------------------------------------------------------

set -euo pipefail

# ---------------------------- defaults -------------------------------------
USERS_DEFAULT=$(printf 'student%02d ' $(seq 1 20))
USERS="${USERS_DEFAULT}"
SCRIPT_PATH="$(pwd)/arco_load_test.py"
PYTHON_BIN="python3"
JOBS=2
WITH_DIFF=0
COMBINED_OUT="$(pwd)/combined_results.jsonl"
STAGGER=0

# ---------------------------- parse flags -----------------------------------
while getopts "u:s:p:j:do:w:h" opt; do
  case "$opt" in
    u) USERS="$OPTARG" ;;
    s) SCRIPT_PATH="$OPTARG" ;;
    p) PYTHON_BIN="$OPTARG" ;;
    j) JOBS="$OPTARG" ;;
    d) WITH_DIFF=1 ;;
    o) COMBINED_OUT="$OPTARG" ;;
    w) STAGGER="$OPTARG" ;;
    h)
      grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown option" >&2
      exit 1
      ;;
  esac
done

if [[ ! -f "$SCRIPT_PATH" ]]; then
  echo "ERROR: script not found at $SCRIPT_PATH" >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
PIDS=()
RESULT_FILES=()

echo "Launching ARCO load test"
echo "  script     : $SCRIPT_PATH"
echo "  python     : $PYTHON_BIN"
echo "  jobs/user  : $JOBS"
echo "  with-diff  : $WITH_DIFF"
echo "  users      : $USERS"
echo "  timestamp  : $TIMESTAMP"
echo

# ---------------------------- launch one process per user -------------------
for USER in $USERS; do
  USER_HOME=$(eval echo "~$USER")

  if [[ ! -d "$USER_HOME" ]]; then
    echo "WARNING: home directory for '$USER' not found ($USER_HOME), skipping" >&2
    continue
  fi

  LOG_DIR="${USER_HOME}/dask-logs/${TIMESTAMP}"
  RESULTS_FILE="${USER_HOME}/arco_load_test_results_${TIMESTAMP}.jsonl"
  STDOUT_LOG="${USER_HOME}/arco_load_test_${TIMESTAMP}.out"
  RESULT_FILES+=("$RESULTS_FILE")

  EXTRA_ARGS=""
  if [[ "$WITH_DIFF" -eq 1 ]]; then
    EXTRA_ARGS="--with-diff"
  fi

  echo "  -> $USER  (log dir: $LOG_DIR)"

  sudo -u "$USER" -H bash -c "
    mkdir -p '$LOG_DIR'
    '$PYTHON_BIN' '$SCRIPT_PATH' \
      --run-id '$USER' \
      --jobs '$JOBS' \
      --log-dir '$LOG_DIR' \
      --results-file '$RESULTS_FILE' \
      $EXTRA_ARGS
  " > "$STDOUT_LOG" 2>&1 &

  PIDS+=($!)

  if [[ "$STAGGER" -gt 0 ]]; then
    sleep "$STAGGER"
  fi
done

echo
echo "Launched ${#PIDS[@]} concurrent run(s). Waiting for completion..."

# ---------------------------- wait for all to finish -------------------------
FAILED=0
for PID in "${PIDS[@]}"; do
  if ! wait "$PID"; then
    FAILED=$((FAILED + 1))
  fi
done

echo "All runs finished. Failures: $FAILED"

# ---------------------------- combine results --------------------------------
: > "$COMBINED_OUT"
for RF in "${RESULT_FILES[@]}"; do
  if [[ -f "$RF" ]]; then
    cat "$RF" >> "$COMBINED_OUT"
  else
    echo "WARNING: missing results file $RF" >&2
  fi
done

echo "Combined results written to: $COMBINED_OUT"
echo "Inspect with, e.g.:"
echo "  python3 -c \"import pandas as pd; print(pd.read_json('$COMBINED_OUT', lines=True))\""

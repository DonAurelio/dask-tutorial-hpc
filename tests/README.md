# ARCO NDVI Load Test

Load-testing toolkit for the ARCO (Analysis-Ready, Cloud-Optimized) NDVI use
case: each simulated "student" spins up its own Dask `SLURMCluster`, streams
the Sentinel-2 Zarr store from OSN, computes NDVI (and optionally the
time-difference NDVI), then tears the cluster down. Results are logged so you
can see how cluster setup time and compute time scale with concurrency.

## Files

| File                     | Purpose                                                                 |
|--------------------------|--------------------------------------------------------------------------|
| `arco_load_test_2.py`    | Single-run worker script: creates cluster, opens ARCO store, computes NDVI, logs timings to a JSON-lines file. |
| `run_arco_load_test.sh`  | Batch launcher: runs `arco_load_test_2.py` concurrently as multiple Linux users via `sudo -u`, then combines all results into one file. |

## Prerequisites

- `run_arco_load_test.sh` must be run as **root** (or a user with `sudo`
  rights to switch to every target user).
- `arco_load_test_2.py` must be **readable** by every target user (e.g. keep
  it under a world-readable path like `/home/data/`).
- The Python interpreter passed via `-p` (e.g.
  `/opt/jupyterhub/bin/python`) must have `dask_jobqueue`, `xarray`, and
  `s3fs` installed, and must be usable by every target user.
- Each target user's `$HOME` must exist and be writable by that user — the
  script writes its per-user Dask worker logs and results file there.

## Usage

### Small test run (3 users)

```bash
sudo bash /home/data/run_arco_load_test.sh \
  -u "ss1 ss2 ss3" \
  -s /home/data/arco_load_test_2.py \
  -p /opt/jupyterhub/bin/python \
  -j 2 -d \
  -o /home/data/results_$(date +%Y%m%d_%H%M%S).jsonl
```

### Larger concurrency run (200 users: `ss1` … `ss200`)

```bash
sudo bash /home/data/run_arco_load_test.sh \
  -u "$(printf 'ss%s ' {1..200})" \
  -s /home/data/arco_load_test_2.py \
  -p /opt/jupyterhub/bin/python \
  -j 2 -d \
  -o /home/data/results_$(date +%Y%m%d_%H%M%S).jsonl
```

### Flags

| Flag | Meaning | Default |
|------|---------|---------|
| `-u "user1 user2 ..."` | Space-separated list of Linux usernames to launch as | `student01..student20` |
| `-s /path/to/script.py` | Path to `arco_load_test_2.py` | `./arco_load_test.py` |
| `-p python_bin` | Python interpreter to use | `python3` |
| `-j N` | `--jobs` (Dask worker jobs per user/cluster) | `2` |
| `-d` | Also compute the time-difference NDVI (extra load) | off |
| `-o /path/combined.jsonl` | Where to write the combined results file | `./combined_results.jsonl` |
| `-w SECONDS` | Stagger launches by N seconds instead of all-at-once | `0` (max concurrency) |

> ⚠️ For large `-u` lists (e.g. 200 users), make sure all 200 accounts
> actually exist and have valid home directories — users without a home
> directory are skipped with a warning.

## What each run produces

Per user (under `$HOME` of that user):

- `dask-logs/<timestamp>/` — Slurm worker job logs for that user's cluster.
- `arco_load_test_results_<timestamp>.jsonl` — one JSON record with timings
  for that user's run.
- `arco_load_test_<timestamp>.out` — combined stdout/stderr of the Python
  process.

After all runs finish, the launcher concatenates every user's results file
into the combined output file given via `-o`.

## Result record fields

Each line of the `.jsonl` output is one JSON object with:

| Field | Description |
|-------|-------------|
| `run_id` | Username / identifier for this run |
| `status` | `success` or `error` |
| `cluster_setup_seconds` | Time to create the `SLURMCluster` and `Client` |
| `open_store_seconds` | Time to open the ARCO Zarr store |
| `ndvi_compute_seconds` | Time for `.compute()` on the NDVI for `time=0` |
| `ndvi_diff_compute_seconds` | Time for the time-diff NDVI (only if `-d` was used) |
| `teardown_seconds` | Time to close client/cluster |
| `total_wallclock_seconds` | End-to-end time for the whole run |
| `error` / `traceback` | Present only if `status == "error"` |

## Analyzing results

```python
import pandas as pd

df = pd.read_json("/home/data/results_20260615_193500.jsonl", lines=True)

# Quick overview
print(df[["run_id", "status", "cluster_setup_seconds",
          "ndvi_compute_seconds", "total_wallclock_seconds"]])

# Did anything fail?
print(df[df["status"] == "error"][["run_id", "error"]])

# Distribution of compute time under load
df["ndvi_compute_seconds"].describe()
```

## Troubleshooting

- **`KeyError: 'JUPYTERHUB_USER'`** — fixed in `arco_load_test_2.py` by
  wrapping `client.dashboard_link` in a try/except (the dashboard link isn't
  needed for the load test and isn't resolvable outside a JupyterHub
  session).
- **Runs skipped with "home directory not found"** — the user account exists
  but has no `$HOME`; create it (e.g. `mkhomedir_helper <user>`) or fix
  `/etc/passwd`.
- **Slow `cluster_setup_seconds` under high concurrency** — expected; this is
  one of the metrics the load test is meant to capture (Slurm scheduling
  contention as many clusters are requested at once).

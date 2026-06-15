#!/usr/bin/env python3
"""
arco_load_test.py

Single-run load-test script for the ARCO (Analysis-Ready, Cloud-Optimized)
NDVI use case (Notebook 5 / "5_Use_case_ARCO").

What it does, in order:
  1. Creates a Dask SLURMCluster and scales it to N worker jobs.
  2. Opens the public ARCO Zarr store on OSN (anonymous S3 access).
  3. Builds the lazy NDVI computation.
  4. Triggers the distributed computation (.compute()) and times it.
  5. Optionally computes the time-difference NDVI as extra load.
  6. Releases the cluster.
  7. Appends a one-line JSON record with timings/metadata to a results file.

Designed to be launched many times concurrently (e.g. from a batch/array
script, one process per "student"). Each run:
  - gets its own SLURMCluster (own scheduler/dashboard, random ports),
  - writes its own Slurm worker-job log directory (so logs don't collide),
  - appends its result line to a shared (or per-run) JSON-lines file.

Usage examples
--------------
Single run, default settings:
    python arco_load_test.py --run-id 1

Heavier load (more workers, also compute the time-diff NDVI):
    python arco_load_test.py --run-id 7 --jobs 4 --with-diff

Custom output locations (useful when launched concurrently):
    python arco_load_test.py --run-id $SLURM_ARRAY_TASK_ID \
        --log-dir /home/$USER/dask-logs/run_$SLURM_ARRAY_TASK_ID \
        --results-file /home/$USER/load_test_results.jsonl
"""

import argparse
import json
import os
import socket
import time
import traceback
from datetime import datetime, timezone

import s3fs
import xarray as xr
from dask_jobqueue import SLURMCluster
from dask.distributed import Client


# --------------------------------------------------------------------------- #
# ARCO store location (public, anonymous read)
# --------------------------------------------------------------------------- #
OSN_ENDPOINT = "https://umn1.osn.mghpcc.org"
ZARR_PATH = "colombia-radar-arco/sentinel2-ard/T18NYM_20200205_20200210.zarr"


def parse_args():
    p = argparse.ArgumentParser(description="ARCO NDVI load-test run")
    p.add_argument("--run-id", default=None,
                    help="Identifier for this run (e.g. student id / array "
                         "task id). Used in log paths and the results record. "
                         "Defaults to '<hostname>-<pid>'.")
    p.add_argument("--jobs", type=int, default=2,
                    help="Number of SLURM worker jobs to scale the cluster "
                         "to (default: 2, matching the notebook).")
    p.add_argument("--cores", type=int, default=1,
                    help="Cores per worker job (default: 1).")
    p.add_argument("--memory", default="8GB",
                    help="Memory per worker job (default: 8GB).")
    p.add_argument("--queue", default=None,
                    help="SLURM partition/queue to submit worker jobs to "
                         "(default: cluster default).")
    p.add_argument("--with-diff", action="store_true",
                    help="Also compute the time(1) - time(0) NDVI "
                         "difference, adding extra load (matches notebook "
                         "section 1.8).")
    p.add_argument("--log-dir", default=None,
                    help="Directory for SLURM worker job logs "
                         "(default: ./dask-logs/<run-id>).")
    p.add_argument("--results-file", default="arco_load_test_results.jsonl",
                    help="Path to a JSON-lines file that this run's result "
                         "record is appended to (default: "
                         "arco_load_test_results.jsonl in the cwd). Safe for "
                         "concurrent appends from multiple processes.")
    p.add_argument("--wait-for-workers", type=int, default=0,
                    help="Seconds to wait for at least one worker to "
                         "register before opening the store (default: 0, "
                         "i.e. don't wait -- Dask will queue tasks until "
                         "workers arrive).")
    return p.parse_args()


def main():
    args = parse_args()

    run_id = args.run_id or f"{socket.gethostname()}-{os.getpid()}"
    log_dir = args.log_dir or os.path.join("dask-logs", str(run_id))
    os.makedirs(log_dir, exist_ok=True)

    record = {
        "run_id": run_id,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "jobs": args.jobs,
        "cores": args.cores,
        "memory": args.memory,
        "with_diff": args.with_diff,
        "start_time_utc": datetime.now(timezone.utc).isoformat(),
        "status": "started",
    }

    cluster = None
    client = None
    t0 = time.perf_counter()

    try:
        # ------------------------------------------------------------- #
        # 1. Create and scale the cluster
        # ------------------------------------------------------------- #
        t_cluster_start = time.perf_counter()

        slurm_kwargs = dict(
            cores=args.cores,
            memory=args.memory,
            processes=True,
            scheduler_options={"dashboard_address": ":0"},
            log_directory=log_dir,
        )
        if args.queue:
            slurm_kwargs["queue"] = args.queue

        cluster = SLURMCluster(**slurm_kwargs)
        cluster.scale(jobs=args.jobs)

        client = Client(cluster)

        if args.wait_for_workers > 0:
            client.wait_for_workers(n_workers=1, timeout=args.wait_for_workers)

        t_cluster_ready = time.perf_counter()
        record["cluster_setup_seconds"] = round(t_cluster_ready - t_cluster_start, 4)

        # client.dashboard_link can raise (e.g. KeyError: 'JUPYTERHUB_USER')
        # when running outside of a JupyterHub session, since distributed
        # tries to format a JupyterHub-proxy URL template using env vars
        # that aren't set for plain `sudo -u ...` runs. It's not needed for
        # the load test, so don't let it abort the run.
        try:
            record["dashboard_link"] = client.dashboard_link
        except Exception as exc:
            record["dashboard_link"] = None
            record["dashboard_link_error"] = str(exc)

        record["scheduler_address"] = client.scheduler.address

        # ------------------------------------------------------------- #
        # 2. Open the ARCO Zarr store (anonymous S3 / OSN)
        # ------------------------------------------------------------- #
        t_open_start = time.perf_counter()

        fs = s3fs.S3FileSystem(
            anon=True,
            client_kwargs={"endpoint_url": OSN_ENDPOINT},
        )
        store = s3fs.S3Map(ZARR_PATH, s3=fs, check=False)
        ds = xr.open_zarr(store, consolidated=False)  # lazy, dask-backed

        t_open_done = time.perf_counter()
        record["open_store_seconds"] = round(t_open_done - t_open_start, 4)

        # ------------------------------------------------------------- #
        # 3. Build the lazy NDVI computation
        # ------------------------------------------------------------- #
        refl = ds.reflectance.astype("float32")
        nir = refl.sel(band="b08")
        red = refl.sel(band="b04")

        denom = nir + red
        ndvi = ((nir - red) / denom).where(denom > 0)  # mask 0/0 nodata

        # ------------------------------------------------------------- #
        # 4. Trigger the distributed computation
        # ------------------------------------------------------------- #
        t_compute_start = time.perf_counter()
        result = ndvi.isel(time=0).compute()
        t_compute_done = time.perf_counter()

        record["ndvi_compute_seconds"] = round(t_compute_done - t_compute_start, 4)
        record["result_shape"] = list(result.shape)

        # ------------------------------------------------------------- #
        # 5. (Optional) extra load: time-difference NDVI
        # ------------------------------------------------------------- #
        if args.with_diff:
            t_diff_start = time.perf_counter()
            ndvi_diff = (ndvi.isel(time=1) - ndvi.isel(time=0)).compute()
            t_diff_done = time.perf_counter()

            record["ndvi_diff_compute_seconds"] = round(t_diff_done - t_diff_start, 4)
            record["diff_shape"] = list(ndvi_diff.shape)

        record["status"] = "success"

    except Exception as exc:
        record["status"] = "error"
        record["error"] = str(exc)
        record["traceback"] = traceback.format_exc()

    finally:
        # ------------------------------------------------------------- #
        # 6. Release the cluster resources
        # ------------------------------------------------------------- #
        t_teardown_start = time.perf_counter()
        try:
            if client is not None:
                client.close()
            if cluster is not None:
                cluster.close()
        except Exception as exc:
            record.setdefault("teardown_error", str(exc))
        t_teardown_done = time.perf_counter()

        record["teardown_seconds"] = round(t_teardown_done - t_teardown_start, 4)
        record["total_wallclock_seconds"] = round(t_teardown_done - t0, 4)
        record["end_time_utc"] = datetime.now(timezone.utc).isoformat()

        # ------------------------------------------------------------- #
        # 7. Append the result record (one JSON object per line)
        # ------------------------------------------------------------- #
        with open(args.results_file, "a") as f:
            f.write(json.dumps(record) + "\n")

        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()

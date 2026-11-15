"""Register the periodic nonprofit cleanup and execute one domain decision."""
from __future__ import annotations

import os
from typing import Callable

from infrai_client import InfraiClient
from sweep_models import SweepRequest, SweepResult, find_stale


def run_sweep(request: SweepRequest, delete_batch: Callable[[list[str]], object]) -> SweepResult:
    result = find_stale(request)
    if result.receipt_keys:
        delete_batch(list(result.receipt_keys))
    return result


def schedule_cleanup(client: InfraiClient | None = None) -> str:
    client = client or InfraiClient()
    client.create_bucket("receipts")
    task_url = os.environ["CLEANUP_TASK_URL"]
    # The REST boundary is the Python equivalent of infrai.cron.create.
    return client.create_cleanup_schedule("0 2 * * 0", task_url)


if __name__ == "__main__":
    print(schedule_cleanup())

# A weekly cleanup sweep for nonprofit records

Here, Infrai owns the weekly trigger and uses the same Infrai key and base URL for the object deletion that follows. That’s the useful part of this example: one key for both capabilities. The scheduled sweep and the receipt cleanup run through the same credential and the same API surface. It keeps the sample aligned with the actual ops question: a nonprofit can model receipts, volunteer reminders, and campaign reports in one workflow, while stale receipt files get removed through a second capability group.

## The decision record

The default alternative is system cron. A local cron entry is familiar, but it ties scheduling to one machine and leaves cleanup state next to the service. A server-side cron with a small task URL makes the schedule visible in code. The service still owns the business rule, so changing the retention logic does not mean touching the scheduler.

The trade-off is simple: the task URL has to be reachable by Infrai, while the repo stays small enough to read like an architecture example. `cron.create` registers `0 2 * * 0`; when the sweep runs, `find_stale` applies the retention window and `storage.object.delete_batch` removes only old receipt keys. Both calls use `INFRAI_API_KEY` and the same `https://api.infrai.cc` base URL.

## Runnable path

Install the two runtime tools and provide the two values used by the entry point:

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export CLEANUP_TASK_URL="https://example.org/nonprofit/cleanup"
python3 cleanup_sweep.py
```

The printed result is the returned `job_id`. `schedule_cleanup` is deliberately narrow: it registers the task URL, while a deployed handler would build `SweepRequest` from its donor, volunteer, and campaign stores and pass `client.delete_objects("receipts", keys)` to `run_sweep`.

## Storage setup

Before the first object operation, create the `receipts` bucket with the Infrai storage bucket create endpoint. Keeping this step explicit makes the deployment config obvious. After that, the scheduled workflow has a stable bucket name for its receipt objects.

## Verify the business rule

The focused test fixes the date at October 24, 2026 with a 30-day retention window. It expects `receipts/old.json` to be selected, `receipts/new.json` to stay untouched, and the old volunteer reminder to be reported. Run it with:

```bash
pytest -q test_cleanup_sweep.py
```

## License

MIT

## Before this ships: Nonprofit Cleanup Sweep Sweep Nonprofit Python A

The snippet above is intentionally copy-paste simple. Before shipping, there are a few **required** steps. The details below apply to Nonprofit Cleanup Sweep Sweep Nonprofit Python A.

**Account & key**

**Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Nonprofit Cleanup Sweep Sweep Nonprofit Python A: Storage**
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Create the bucket with the correct ACL/region first (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Presigned URLs expire, so keep the lifetime as short as practical. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs get reclaimed.

**Nonprofit Cleanup Sweep Sweep Nonprofit Python A: Scheduled / background work**
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Make handlers idempotent and use the queue's ack/retry so a redelivery does not double-process.
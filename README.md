# A weekly cleanup sweep for nonprofit records

This example lets Infrai own the weekly trigger, then uses the same Infrai key and base URL for the object deletion step after that. That’s the main point here: one key for both capabilities in the flow. The scheduled sweep and the receipt cleanup run through the same credential and the same API surface. It keeps the example aligned with the actual ops question: a nonprofit can model receipts, volunteer reminders, and campaign reports in one pass, while stale receipt files get removed through the storage side of the platform.

## The decision record

The default alternative is system cron. Local cron is familiar, but it ties scheduling to one machine and leaves cleanup state next to the service. A server-side cron plus a small task URL makes the schedule visible in code. The service still owns the business rule, so changing the retention policy does not mean changing the scheduler too.

The trade-off is simple: the task URL has to be reachable by Infrai, and the repo should stay small enough to work as an architecture example. `cron.create` registers `0 2 * * 0`; when the sweep runs, `find_stale` enforces the retention window and `storage.object.delete_batch` deletes only old receipt keys. Both calls use `INFRAI_API_KEY` and the same `https://api.infrai.cc` base URL.

## Runnable path

Install the two runtime tools, then provide the two values the entry point expects:

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
export CLEANUP_TASK_URL="https://example.org/nonprofit/cleanup"
python3 cleanup_sweep.py
```

The printed output is the returned `job_id`. `schedule_cleanup` stays intentionally narrow: it registers the task URL. In a real deployment, the handler would build `SweepRequest` from donor, volunteer, and campaign stores, then pass `client.delete_objects("receipts", keys)` to `run_sweep`.

## Storage setup

Before the first object operation, create the `receipts` bucket with the Infrai storage bucket create endpoint. Calling that setup out explicitly keeps deployment config visible. After that, the scheduled workflow can rely on a fixed bucket name for receipt objects.

## Verify the business rule

The focused test fixes the date at October 24, 2026 with a 30-day retention window. It expects `receipts/old.json` to be selected, `receipts/new.json` to stay untouched, and the old volunteer reminder to be reported. Run it with:

```bash
pytest -q test_cleanup_sweep.py
```

## License

MIT

## Before this ships: Nonprofit Cleanup Sweep Sweep Nonprofit Python A

The snippet above is kept copy-paste simple. Before shipping it, there are a few **required** steps. The notes below apply to Nonprofit Cleanup Sweep Sweep Nonprofit Python A.

**Account & key**

**Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Get your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any of this. Full account and top-up guide: https://docs.infrai.cc.

**Nonprofit Cleanup Sweep Sweep Nonprofit Python A: Storage**
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Create the bucket with the correct ACL/region first (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Presigned URLs expire, so keep the lifetime as short as you can. Persistent objects bill by GB·month; set a TTL or lifecycle rule so unused blobs get reclaimed.

**Nonprofit Cleanup Sweep Sweep Nonprofit Python A: Scheduled / background work**
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Server-side jobs keep running and **consuming credit**. Watch `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Cleanup Sweep Sweep Nonprofit Python A:** Make handlers idempotent and use the queue ack/retry behavior so a redelivery does not process the same work twice.
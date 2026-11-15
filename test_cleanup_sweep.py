from datetime import date

from cleanup_sweep import run_sweep
from sweep_models import CampaignReport, DonorReceipt, SweepRequest, VolunteerReminder


def test_sweep_deletes_only_records_older_than_retention_window() -> None:
    request = SweepRequest(
        today=date(2026, 10, 24),
        retention_days=30,
        receipts=(
            DonorReceipt("old", date(2026, 9, 1), "receipts/old.json"),
            DonorReceipt("new", date(2026, 10, 1), "receipts/new.json"),
        ),
        reminders=(VolunteerReminder("v-old", date(2026, 9, 1)),),
        reports=(CampaignReport("campaign-current", date(2026, 10, 1)),),
    )
    deleted: list[list[str]] = []

    result = run_sweep(request, deleted.append)

    assert result.receipt_keys == ("receipts/old.json",)
    assert result.reminder_ids == ("v-old",)
    assert result.report_ids == ()
    assert deleted == [["receipts/old.json"]]


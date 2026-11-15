"""Typed nonprofit records and the cleanup decision."""
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DonorReceipt:
    receipt_id: str
    issued_on: date
    object_key: str


@dataclass(frozen=True)
class VolunteerReminder:
    volunteer_id: str
    due_on: date


@dataclass(frozen=True)
class CampaignReport:
    campaign_id: str
    last_reported_on: date


@dataclass(frozen=True)
class SweepRequest:
    today: date
    retention_days: int
    receipts: tuple[DonorReceipt, ...]
    reminders: tuple[VolunteerReminder, ...]
    reports: tuple[CampaignReport, ...]


@dataclass(frozen=True)
class SweepResult:
    receipt_keys: tuple[str, ...]
    reminder_ids: tuple[str, ...]
    report_ids: tuple[str, ...]


def find_stale(request: SweepRequest) -> SweepResult:
    cutoff = request.today.toordinal() - request.retention_days
    return SweepResult(
        receipt_keys=tuple(r.object_key for r in request.receipts if r.issued_on.toordinal() < cutoff),
        reminder_ids=tuple(r.volunteer_id for r in request.reminders if r.due_on.toordinal() < cutoff),
        report_ids=tuple(r.campaign_id for r in request.reports if r.last_reported_on.toordinal() < cutoff),
    )


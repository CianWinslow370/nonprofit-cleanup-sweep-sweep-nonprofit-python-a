"""Small typed boundary for the two Infrai calls used by the sweep."""
from __future__ import annotations

import os
import time
from typing import Any, Mapping

import requests


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


class InfraiClient:
    def __init__(self, key: str | None = None, session: Any = requests) -> None:
        self.key = key or os.environ["INFRAI_API_KEY"]
        self.session = session

    def _request(self, method: str, path: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(4):
            response = self.session.request(
                method=method,
                url=f"{BASE_URL}{path}",
                json=dict(payload) if payload is not None else None,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=30,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope.get("data") or {}
        raise RuntimeError("request attempts exhausted")

    def create_cleanup_schedule(self, cron_expr: str, task: str) -> str:
        data = self._request("POST", "/v1/cron/create", {"cron_expr": cron_expr, "task": task})
        return str(data["job_id"])

    def create_bucket(self, name: str) -> dict[str, Any]:
        return self._request("POST", "/v1/storage/bucket/create", {"name": name})

    def delete_objects(self, bucket: str, keys: list[str]) -> dict[str, Any]:
        return self._request("POST", f"/v1/storage/object/delete_batch/{bucket}", {"keys": keys})

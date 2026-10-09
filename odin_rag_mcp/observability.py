"""Observability helpers for request tracing and latency metrics."""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass


@dataclass
class RequestTrace:
    """Represents a single traced HTTP request."""

    trace_id: str
    method: str
    path: str
    client_ip: str
    status_code: int
    duration_ms: float
    timestamp: float


class ObservabilityRegistry:
    """Thread-safe registry for request traces and latency metrics."""

    def __init__(self) -> None:
        self._traces: list[RequestTrace] = []
        self._lock = threading.Lock()
        self._total_requests = 0
        self._total_latency_ms = 0.0

    def new_trace_id(self) -> str:
        """Generate a stable trace identifier for the current request."""
        return uuid.uuid4().hex

    def record_request(
        self,
        *,
        method: str,
        path: str,
        client_ip: str,
        status_code: int,
        duration_ms: float,
        trace_id: str | None = None,
    ) -> RequestTrace:
        """Persist a request trace and update aggregate latency counters."""
        resolved_trace_id = trace_id or self.new_trace_id()
        entry = RequestTrace(
            trace_id=resolved_trace_id,
            method=method,
            path=path,
            client_ip=client_ip,
            status_code=status_code,
            duration_ms=duration_ms,
            timestamp=time.time(),
        )

        with self._lock:
            self._traces.append(entry)
            self._traces = self._traces[-100:]
            self._total_requests += 1
            self._total_latency_ms += duration_ms

        return entry

    def snapshot(self) -> dict[str, float | int | list[dict[str, float | int | str]]]:
        """Return aggregate metrics and recent traces for monitoring endpoints."""
        with self._lock:
            total = self._total_requests
            average_latency_ms = (self._total_latency_ms / total) if total else 0.0
            recent = [
                {
                    "trace_id": item.trace_id,
                    "method": item.method,
                    "path": item.path,
                    "client_ip": item.client_ip,
                    "status_code": item.status_code,
                    "duration_ms": round(item.duration_ms, 3),
                    "timestamp": item.timestamp,
                }
                for item in self._traces[-10:]
            ]
            return {
                "total_requests": total,
                "average_latency_ms": round(average_latency_ms, 3),
                "recent_traces": recent,
            }


observability = ObservabilityRegistry()

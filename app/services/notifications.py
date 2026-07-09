"""Side effects that accompany booking lifecycle events.

Each booking change sends a (simulated) notification email and appends an
audit-log entry. Both resources are guarded by a single lock so their output
stays consistent when many requests are processed at once.
"""
import threading

_lock = threading.Lock()


def _send_email(kind: str, booking) -> None:
    pass


def _write_audit(kind: str, booking) -> None:
    pass


def notify_created(booking) -> None:
    with _lock:
        _write_audit("created", booking)
        _send_email("created", booking)


def notify_cancelled(booking) -> None:
    with _lock:
        _write_audit("cancelled", booking)
        _send_email("cancelled", booking)
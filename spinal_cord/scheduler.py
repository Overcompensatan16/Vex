"""Event-driven scheduler used by the spinal cord simulation.

The scheduler operates on a monotonic notion of time and stores future
callbacks in a priority queue.  Each scheduled callback is invoked when
:func:`run_until` advances simulation time beyond the callback's scheduled
timestamp.  Earlier timestamps run first; callbacks sharing the same timestamp
are ordered by ascending ``priority`` and finally by insertion order.  The
module exposes a small API that supports cancellation, resilient execution of
callbacks that raise exceptions, recurring events, and configurable
timekeeping (floating-point milliseconds by default or integer microseconds
for long-running simulations).
"""

from __future__ import annotations

import heapq
import logging
from itertools import count
from typing import Any, Callable, List, Optional, Tuple, Union

__all__ = [
    "schedule",
    "schedule_repeating",
    "run_until",
    "cancel",
    "configure_timebase",
    "now",
]

logger = logging.getLogger(__name__)

TimeValue = Union[float, int]

# ``now`` is intentionally exposed at module level so tests and other modules
# can inspect the scheduler's notion of current time.
now: TimeValue = 0.0

# The priority queue stores tuples of
# (time, priority, insertion_index, callable, args, interval, event_id).
_event_queue: List[
    Tuple[
        TimeValue,
        float,
        int,
        Callable[..., Any],
        Tuple[Any, ...],
        Optional[TimeValue],
        int,
    ]
] = []
_counter = count()
_event_ids = count(1)
_cancelled_event_ids: set[int] = set()
_live_event_ids: set[int] = set()
_use_integer_microseconds = False


def configure_timebase(*, integer_microseconds: bool = False) -> None:
    """Configure the scheduler's internal time representation.

    Args:
        integer_microseconds: When ``True`` the scheduler rounds all supplied
            timestamps and intervals to integer microseconds.  When ``False``
            (the default) times are represented as floating-point milliseconds.

    Raises:
        RuntimeError: If called while events are queued; pending events cannot
            be converted between time bases safely.
    """

    global now, _use_integer_microseconds

    if _event_queue:
        raise RuntimeError("Cannot reconfigure timebase while events are queued")

    _use_integer_microseconds = bool(integer_microseconds)
    now = _coerce_time(now)


def _coerce_time(value: Any) -> TimeValue:
    """Return ``value`` coerced into the active time representation."""

    if _use_integer_microseconds:
        # Round to the nearest integer microsecond to reduce cumulative drift.
        return int(round(float(value)))
    return float(value)


def _coerce_interval(value: Any) -> TimeValue:
    """Validate and normalize interval inputs."""

    interval = _coerce_time(value)
    if interval <= 0:
        raise ValueError("Interval must be greater than zero")
    return interval


def _schedule_event(
    time_point: Any,
    priority: float,
    fn: Callable[..., Any],
    args: Tuple[Any, ...],
    interval: Optional[Any],
    *,
    event_id: Optional[int] = None,
) -> int:
    if not callable(fn):  # pragma: no cover - defensive programming
        raise TypeError("Scheduled function must be callable")

    normalized_time = _coerce_time(time_point)
    normalized_interval: Optional[TimeValue] = None
    if interval is not None:
        normalized_interval = _coerce_interval(interval)

    if event_id is None:
        event_id = next(_event_ids)

    event = (
        normalized_time,
        float(priority),
        next(_counter),
        fn,
        args,
        normalized_interval,
        event_id,
    )
    heapq.heappush(_event_queue, event)
    _live_event_ids.add(event_id)
    return event_id


def schedule(time_ms: float, priority: float, fn: Callable[..., Any], *args: Any) -> int:
    """Schedule ``fn`` to run at ``time_ms`` with ``priority``.

    Args:
        time_ms: Timestamp at which ``fn`` should fire.  Units follow the active
            time base (milliseconds by default or microseconds when configured).
        priority: Lower numbers run before higher ones when timestamps match.
        fn: Callable invoked as ``fn(time_ms, *args)`` when the event fires.
        *args: Additional arguments forwarded to ``fn``.

    Raises:
        TypeError: If ``fn`` is not callable.

    Returns:
        A unique token that can be supplied to :func:`cancel` to inhibit the
        event before it fires.
    """

    return _schedule_event(time_ms, priority, fn, args, interval=None)


def schedule_repeating(
    interval: float,
    fn: Callable[..., Any],
    *args: Any,
    priority: float = 0.0,
    start_time: Optional[float] = None,
) -> int:
    """Schedule ``fn`` to run repeatedly every ``interval`` units of time.

    The first invocation is scheduled for ``start_time + interval`` (or
    ``now + interval`` when ``start_time`` is omitted).  The callback is invoked
    as ``fn(scheduled_time, *args)`` for each firing.

    Args:
        interval: Delay between invocations.  Units match the active time base
            (milliseconds by default or microseconds when configured).
        fn: Callable to execute when the event fires.
        *args: Additional positional arguments forwarded to ``fn``.
        priority: Optional priority for tie-breaking with other events.
        start_time: Optional explicit starting point for the sequence.  When
            omitted, the sequence begins relative to the current :data:`now`.

    Returns:
        A unique token suitable for :func:`cancel`.
    """

    base_time = now if start_time is None else _coerce_time(start_time)
    interval_value = _coerce_interval(interval)
    first_fire = _coerce_time(base_time + interval_value)
    return _schedule_event(first_fire, priority, fn, args, interval_value)


def run_until(t_stop: float) -> None:
    """Advance the scheduler and execute all events due by ``t_stop``.

    Args:
        t_stop: Simulation time to advance to.  Units follow the active time
            base and must be greater than or equal to the current :data:`now`
            value.

    Raises:
        ValueError: If ``t_stop`` is earlier than the scheduler's ``now``.
    """

    global now

    target_time = _coerce_time(t_stop)
    if target_time < now:
        raise ValueError("Cannot run scheduler backwards in time")

    while _event_queue and _event_queue[0][0] <= target_time:
        event_time, priority, _, fn, args, interval, event_id = heapq.heappop(
            _event_queue
        )
        now = event_time

        if event_id in _cancelled_event_ids:
            _cancelled_event_ids.discard(event_id)
            _live_event_ids.discard(event_id)
            continue

        try:
            fn(event_time, *args)
        except Exception:  # pragma: no cover - logging side-effect only
            logger.exception(
                "Scheduler event %s (id=%s) failed at %s",
                getattr(fn, "__name__", repr(fn)),
                event_id,
                event_time,
            )

        if interval is not None and event_id not in _cancelled_event_ids:
            next_fire = _coerce_time(event_time + interval)
            _schedule_event(
                next_fire,
                priority,
                fn,
                args,
                interval,
                event_id=event_id,
            )
        else:
            _live_event_ids.discard(event_id)
            _cancelled_event_ids.discard(event_id)

    now = max(now, target_time)


def cancel(event_id: int) -> bool:
    """Cancel a scheduled event.

    Args:
        event_id: Token previously returned by :func:`schedule` or
            :func:`schedule_repeating`.

    Returns:
        ``True`` if the scheduler will suppress future firings of the event,
        ``False`` if the event had already completed or was unknown.
    """

    if event_id not in _live_event_ids:
        return False

    _cancelled_event_ids.add(event_id)
    return True

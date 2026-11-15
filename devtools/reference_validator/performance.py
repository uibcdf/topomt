"""Small opt-in phase/call measurements; no global scientific hooks."""

import cProfile
import resource
import time
from collections.abc import Callable
from copy import deepcopy
from typing import Any, TypeVar

_Result = TypeVar('_Result')


class Measurements:
    """Keep nonoverlapping phase timings, with separately identified profiling.

    Parameters
    ----------
    profile : bool
        Enable call profiling. These timings include instrumentation overhead.
    """

    def __init__(self, *, profile: bool = False) -> None:
        self._profile = profile
        self._phases: dict[str, Any] = {}
        self._running = False

    def run(self, name: str, operation: Callable[[], _Result]) -> _Result:
        """Measure one synchronous phase, preserving failures and return values.

        Parameters
        ----------
        name : str
            Unique phase name. Nested phases are rejected to prevent double sums.
        operation : callable
            Bounded caller-owned operation; execution limits remain external.

        Returns
        -------
        object
            The operation's unchanged result.

        Raises
        ------
        ValueError
            Reused or nested phase name. Operation failures propagate unchanged.
        """
        if not name or name in self._phases or self._running:
            raise ValueError('Phase names must be unique and nonoverlapping')
        self._running = True
        profiler = cProfile.Profile() if self._profile else None
        start, cpu = time.monotonic(), time.process_time()
        child = resource.getrusage(resource.RUSAGE_CHILDREN)
        failed = True
        try:
            if profiler is not None:
                profiler.enable()
            result = operation()
            failed = False
            return result
        finally:
            if profiler is not None:
                profiler.disable()
            ended = resource.getrusage(resource.RUSAGE_CHILDREN)
            self._phases[name] = {
                'wall_seconds': time.monotonic() - start,
                'cpu_seconds': time.process_time() - cpu,
                'waited_children_cpu_seconds': (
                    ended.ru_utime + ended.ru_stime - child.ru_utime - child.ru_stime
                ),
                'failed': failed,
                'calls': []
                if profiler is None
                else [
                    {
                        'function': entry.code
                        if isinstance(entry.code, str)
                        else f'{entry.code.co_filename}:{entry.code.co_firstlineno}:{entry.code.co_name}',
                        'calls': entry.callcount,
                        'recursive_calls': entry.reccallcount,
                        'exclusive_seconds': entry.inlinetime,
                        'inclusive_seconds': entry.totaltime,
                    }
                    for entry in profiler.getstats()
                ],
            }
            self._running = False

    def to_record(self) -> dict[str, Any]:
        """Detach timings; inclusive call times must not be added as phases."""
        return {
            'schema': 'topomt.reference-validator.measurements/1',
            'profiled': self._profile,
            'child_cpu_scope': 'terminated-and-waited children only',
            'phases': deepcopy(self._phases),
        }

"""Lazy, cached numba JIT for TopoMT numeric kernels.

Mirrors the molsysmt pattern (``molsysmt/_private/jit.py``): numba is a real
dependency and kernels are compiled lazily on first call and cached on disk
(``cache=True``). Nested ``@lazy_njit`` kernels are rebound to their compiled
dispatchers before the caller is compiled, so a kernel may call another kernel.

The molsysmt parallel-mode / thread-pool / telemetry machinery is intentionally
omitted -- it is coupled to molsysmt's own configuration and catalog. numba is
imported lazily (on first compilation) rather than at module load, so importing
TopoMT does not pull in numba/LLVM unless an accelerated kernel is actually used.
"""

from functools import lru_cache, wraps

_WRAPPER_COMPILED: dict = {}
_COMPILING: set = set()


def lazy_njit(signature=None, cache=True, **kwargs):
    """Return a lazily-compiled njit function (optionally with a fixed signature)."""

    def decorator(func):
        @lru_cache(maxsize=1)
        def _compiled():
            import numba as nb

            jit_kwargs = dict(kwargs)
            jit_kwargs.setdefault('fastmath', True)

            def _build():
                if signature is not None:
                    return nb.njit(signature, cache=cache, **jit_kwargs)(func)
                return nb.njit(cache=cache, **jit_kwargs)(func)

            if wrapper in _COMPILING:
                return _build()
            _COMPILING.add(wrapper)
            try:
                # Bind nested lazy kernels to their compiled dispatchers first.
                for name in func.__code__.co_names:
                    value = func.__globals__.get(name)
                    if (
                        callable(value)
                        and value in _WRAPPER_COMPILED
                        and value is not wrapper
                    ):
                        func.__globals__[name] = _WRAPPER_COMPILED[value]()
                return _build()
            finally:
                _COMPILING.discard(wrapper)

        @wraps(func)
        def wrapper(*args, **kwds):
            return _compiled()(*args, **kwds)

        _WRAPPER_COMPILED[wrapper] = _compiled
        return wrapper

    return decorator

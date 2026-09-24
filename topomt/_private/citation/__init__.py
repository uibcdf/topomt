# topomt/_private/citation/__init__.py
from .._private.optional_import import optional_import

scoped_usage, track_item = optional_import(
    'flowcite',
    ['scoped_usage', 'track_item'],
    fallback={
        'scoped_usage': lambda target=None: lambda fn: fn,
        'track_item': lambda *args, **kwargs: None,
    },
)

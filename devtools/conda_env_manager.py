"""Invoke reviewed shared environment operations with this owner's root."""

import sys

from check_dependency_routes import ROOT, load_sdk


def main() -> int:
    """Delegate explicit commands to the immutable shared CLI."""
    tools = load_sdk('conda_environment_tools')
    sys.argv[1:1] = ['--root', str(ROOT)]
    return tools.main()


if __name__ == '__main__':
    raise SystemExit(main())

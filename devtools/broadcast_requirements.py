"""Generate only explicit owner environments; never parse or rewrite a recipe."""

import sys

from conda_env_manager import main

if __name__ == '__main__':
    sys.argv[1:1] = ['generate']
    raise SystemExit(main())

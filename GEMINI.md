# TopoMT - Project Context for Gemini

## 1. Project Overview
**TopoMT** (Molecular Topography Multi Toolkit) is a Python library for the hierarchical analysis of molecular surface topography. It detects, represents, and analyzes features like pockets, cavities, channels, and interfaces.
*   **Ecosystem:** Part of the MolSysMT ecosystem.
*   **Core Concepts:** Composability, extensibility, robustness (type checking/units).
*   **Key Dependencies:** `MolSysMT`, `PyUnitWizard`, `NumPy`, `SciPy`, `NGLview`.

## 2. Repository Structure
*   `topomt/`: Core source code.
*   `tests/`: Unit and integration tests (`pytest`).
*   `devtools/`: Environment and build tools (`requirements.yaml`, conda envs).
*   `docs/`: Sphinx documentation.
*   `sandbox/`: Experimental notebooks and code.
*   `AGENTS.md`: Detailed rules for AI agents (primary source for behavioral protocols).
*   `pyproject.toml` / `setup.cfg`: Build configuration.

## 3. Development Workflow

### Installation
*   **Python Versions:** 3.10, 3.11, 3.12.
*   **Install (Dev):** Likely `pip install -e .[test]` (standard for `pyproject.toml` projects).

### Testing
*   **Command:** `pytest tests/`
*   **Protocol:**
    *   **Test-First:** Write/update tests before implementing features.
    *   **Bug Fixes:** Reproduce with a failing test first.
    *   **Scope:** All public functions must be tested.

### Formatting & Linting
*   **Tools:** `black`, `isort`, `flake8`, `mypy`.
*   **Style:** PEP 8.
*   **Config:**
    *   `black`: line-length 88, single quotes default.
    *   `flake8`: max-line-length 119.

## 4. Coding Standards (Critical)
*   **Docstrings:** NumPy style. Required for all public symbols (Parameters, Returns, Raises, Examples).
*   **Type Hints:** PEP 484. Required for public functions. Use concrete types (`Path`, `str`) over generic ones. No `from __future__ import annotations`.
*   **Naming:** `snake_case` (vars/funcs), `PascalCase` (classes), `_` prefix (private).
*   **Imports:** Absolute imports preferred? (Not explicitly stated, but standard).
*   **Strings:** Single quotes (`'`) default. Double quotes (`"`) if string contains apostrophe. Triple double quotes (`"""`) for docstrings.

## 5. Agent Operational Rules
*   **Git:**
    *   Commit messages: Conventional Commits (`feat(core): desc`).
    *   No untracked changes.
    *   Confirm with `git status`.
*   **Citations:**
    *   Files: `【F:<path>†L<start>-L<end>】`
    *   Terminal: `【<chunk_id>†L<start>-L<end>】`
*   **Safety:**
    *   **Always Ask Before:** Committing, destructive commands, editing CI/docs/config.
    *   **Allowed:** Linters, tests, generating docs locally.
*   **Behavior:**
    *   Wait for commands to complete.
    *   Propose changes via PR (or simulate PR workflow).
    *   **Do not revert changes** unless explicitly requested.

## 6. Key Commands Reference
*   **Test:** `pytest tests/`
*   **Format:** `black . && isort .`
*   **Lint:** `flake8`
*   **Type Check:** `mypy topomt` (inferred)

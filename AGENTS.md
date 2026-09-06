# TopoMT

*A Python library for the hierarchical analysis of molecular surface topography.*

---

## External Tooling Guides (Required for Development)

These guides are required reading for anyone developing this library. They describe how
external tools must be used here.

- `GH_RUN_RECEPTOR_GUIDE.md` — Required guide for compact, truth-preserving inspection of
  GitHub Actions runs and the native-command fallback.

## 1. Purpose of This File

This file defines how automated agents and human contributors must work with the **TopoMT** repository.  
It serves as a guide for consistent, transparent, and safe collaboration between humans and automated systems.

---

## 2. Project Overview

**TopoMT** is a Python library designed for the hierarchical analysis of molecular
surface topography. It provides a unified framework to identify, classify, and
relate topographical features such as concavities, convexities, interfaces, and
boundaries across biomolecular surfaces. By representing these features through
a structured hierarchy — from local shape elements to higher-order surface
regions — TopoMT enables researchers to quantify molecular geometry, compare
surface architectures, and integrate shape-derived information into
structure-based modeling, drug-design, and biophysical analysis workflows. The
library is developed as part of the MolSysMT ecosystem, ensuring smooth
interoperability with molecular systems, trajectories, and other computational
toolkits for molecular science.

Design principles:

- **Composability:** small, reusable components.
- **Extensibility:** easy to add new feature types or surface descriptors.
- **Robustness:** strict type checking and dimensional consistency.

---

## 3. Repository Structure

Main directories and files:

| Path | Description |
|------|--------------|
| `topomt/` | Core source code. |
| `tests/` | Unit and integration tests. |
| `devtools/` | Environment, build, and maintenance tools. |
| `docs/` | Documentation sources (Sphinx). |
| `sandbox/` | Experimental code and notes. |
| `logos/` | Branding assets. |
| `CODE_OF_CONDUCT.md` | Community standards. |
| `AGENTS.md` | Agent interaction rules (this file). |
| `README.md` | Quick start and overview. |
| `LICENSE` | License information. |
| `MANIFEST.in` | Packaging manifest file. |
| `pyproject.toml` | Build system configuration. |
| `pytest.ini` | Pytest configuration. |
| `setup.cfg` | Setup tools configuration. |

Additional `AGENTS.md` files may exist in submodules with specialized instructions.

### 3.1 Dependencies

Key/Core dependencies:

| Package | Purpose |
|---------|---------|
| MolSysMT | Provides molecular system representation,
topology access, selection, and format conversions. TopoMT builds directly on
MolSysMT data structures and relies on its API for atom-level and surface-level
analysis.|
| PyUnitWizard | Handles physical units and conversions.|
| NumPy | Numerical computations |
| SciPy | Scientific computing |
| NGLview | Molecular visualization |
| pytest | Testing framework |
| Sphinx | Documentation generation |

### 3.2 Python Versions supported

TopoMT is developed and tested for **Python 3.10, 3.11 and 3.12**.
Taking advantage of the latest language features and type hinting improvements for that versions.

---

## 4. Coding Guidelines

### 4.1 General Conventions

- Keep PRs small and focused.  
- Use English for all code, comments, PRs, issues, and docs.  
- Always include or update tests and documentation for user-visible changes.  
- Follow existing patterns and maintain readability.  
- Avoid unnecessary cleverness — clarity first.
- Use the last coding standards for scientific Python projects/libraries.

### 4.2 Code Style

- Follow **PEP 8**.  
- Tools: `ruff format` (formatting), `ruff check` (linting/import sorting), `mypy` (type checking).  
- Prefer short, modular functions.  
- Use explicit, descriptive names.  
- Run linting and type checks before committing.

### 4.3 Naming

| Element | Convention | Example |
|----------|-------------|---------|
| Variables / functions | `snake_case` | `convert_units()` |
| Classes | `PascalCase` | `UnitSystem` |
| Private members | Prefix with `_` | `_parse_symbol()` |
| Boolean-returning | Suffix `_is` / `_has` | `is_valid()`, `has_units()` |

### 4.4 Docstrings

- Use **NumPy style**.  
- Each public symbol must include **Parameters**, **Returns**, **Raises**, and **Examples** when applicable.

### 4.5 Type Annotations

- Annotate all public functions (PEP 484).  
- Use `Optional[T]` for nullable types.  
- Use `Literal` or `Enum` for restricted values.  

### 4.6 Comments

- Explain *why*, not just *what*.  
- Keep comments up to date.  
- Prefer brief, focused notes.  
- Tags: `TODO`, `FIXME`, `NOTE`, `WARNING` (with author/date if long-term).

### 4.7 Error Handling

- Use custom exceptions in `exceptions.py` for domain-specific errors.  
- Never use bare `except:` clauses.  
- Provide clear and informative error messages.

### 4.8 Logging and Warnings

- Use `logging` for runtime messages.  
- Use `_private/warnings` for non-critical issues or deprecations.

### 4.9 Security and Dependencies

- Use only dependencies listed in `devtools/conda-envs/development_env.yaml`.  
- Avoid deprecated or unmaintained packages.  
- Regularly verify that dependencies are **available, necessary, and pertinent**.  
- Check dependencies periodically using tools such as `safety` or `bandit`.  
- Never commit secrets, credentials, or environment variables.  
- Avoid hardcoding sensitive information in code or logs.  
- Do not report or share secrets, credentials, or environment variables in **issues**, **PRs**, or any communication channel.  

### 4.10 String and Quotation Style

Follow these conventions for quotation marks and string formatting.

- Use **single quotes (`'`)** for strings by default.
- Use **double quotes (`"`)** only when the string itself contains an apostrophe.
- Use **triple double quotes (`"""`)** for **docstrings**, both for modules and functions.
- Use double quotes (") when the string itself contains a single quote/apostrophe 
or when double quotes make the string clearer to read. Readability beats blind
consistency.
- When a string already uses double quotes inside, you can define it with single quotes outside.
- When embedding JSON or other data formats that require double quotes by specification, preserve their native quoting style.

### 4.11  Type hints and annotations

- All source code targets **Python ≥3.10**.
- Do **not** use `from __future__ import annotations`.  
  Modern Python already supports deferred evaluation of annotations (PEP 649).
- Do **not** wrap types in quotes (e.g., use `str`, not `'str'`), except for
  forward references to classes defined later in the file or imported under
  `if TYPE_CHECKING:`.
- Prefer explicit type annotations in all public functions and methods.
- Use concrete types (`Path`, `str`, `list[Feature]`, etc.) instead of overly
  generic ones unless generic typing is required.
- Avoid `TypeAlias` and `Protocol` unless strictly necessary for structural typing.

---

## 5. Testing Guidelines

- All public functions and modules must have tests under `tests/`.  
- Use `pytest` for test execution.  
- Run `pytest tests/` before each PR.  
- Test both success and failure cases.  
- Prefer **unit tests** for small functions and **integration tests** for workflows.  
- Keep tests independent and reproducible.  

### 5.1 Test-First Development Mode

- **For new features:** write or update unit tests first, then implement the feature until all tests pass (“code to green”).  
- **For regressions:** add a failing test that reproduces the bug, then fix it.  
- **For UI or state-based modules:** prefer component tests that validate observable changes.  

---

## 6. Documentation Guidelines

- Written in Markdown or MyST (for Sphinx).  
- Each public module must include examples and docstrings.  
- Update documentation after API or behavior changes.  
- Validate generated docs before merging (`make html`).  
- Do not include private or experimental code in public docs.

## 6.1 Docstring Style

- Always use **PEP 257-compliant** docstrings (`"""Triple double quotes"""`).
- Write the first line as a concise summary, followed by a blank line, then a more detailed description if needed.


---

## 7. Version Control and Contributions

### 7.1 Commit Messages

Use the conventional format:

```
<type>(<scope>): <short description>
```

Examples:
- `feat(core): add converter for astropy units`
- `fix(tests): correct numpy array comparison`
- `docs(readme): improve quick-start example`

Keep commits atomic, small, and meaningful.

### 7.2 Pull Requests

- Run all tests before submitting.  
- Ensure lint/type checks pass.  
- Keep PRs under 300 lines of diff when possible.  
- Include context and motivation in the PR body.  
- Link related issues with `Fixes #<id>` or `Closes #<id>`.  

Checklist:
- ✅ All tests and checks pass.  
- ✅ Code reviewed or self-reviewed.  
- ✅ Docs updated if behavior changed.  
- ✅ No debug or leftover code.  

---

## 8. AI Agent Guidelines

These rules apply to automated agents (GitHub Actions, Copilot Agents, CI bots, etc.) collaborating on this repository.

### 8.1 General Behavior

- Always wait for terminal commands to complete before proceeding.  
- Do not modify code outside the assigned scope.  
- Prefer proposing changes via PR rather than direct commits to `main`.  
- Ask for clarification or open a draft PR if unsure.  
- Never overwrite human work or documentation without explicit approval.  
- When stuck, **ask a clarifying question**, propose a short plan, or open a draft PR with notes — do not push large speculative changes without confirmation.  
- If the repository already contains a file with the target pattern, agents should follow that pattern without asking.

### 8.2 Citation Format

When referencing files or terminal outputs in responses, use the following citation style:

1. **File citations:** `【F:<path>†L<start>-L<end>】`  
2. **Terminal citations:** `【<chunk_id>†L<start>-L<end>】`  

Only cite relevant, contentful lines — never blank lines.

If referencing code changes or test results in PR summaries, prefer **file citations**; use terminal citations only when output verification is required.

### 8.3 Git Instructions for Agents

- Commit using `git` (no untracked changes).  
- Fix pre-commit issues before retrying.  
- Do not amend existing commits; create new ones.  
- Confirm with `git status` before finishing.  

### 8.4 Testing Protocol for Agents

- Follow **test-first** development: add or update tests before writing new code.  
- For bug fixes, add a failing test first, then implement the fix.  
- Do not skip tests unless justified in the PR.  

### 8.5 Programmatic Checks for Agents

This section defines automated consistency checks to be performed by AI or CI agents before merging changes.  
To be extended in future versions, it may include:

- Verification of documentation coverage.  
- Automatic code style and dependency audits.  
- Validation of cross-repo synchronization for shared components.  

### 8.6 Safety and Permissions

**Allowed without prompt:**  
- Running linters, formatters, or test suites.  
- Generating documentation locally.  
- Checking dependency status.  

**Ask before doing:**  
- Committing code or modifying configuration.  
- Running destructive commands (e.g., deleting branches or files).  
- Editing documentation or CI pipelines.  
- Updating build/test commands, contribution guidelines, or security considerations.  
- Changing commit message conventions or PR workflows.  

---

## 9. Maintenance Reminders

- After any change, verify if documentation, examples, or tests must be updated.  
- After any change, verify if any `AGENTS.md` or `README.md` need to be updated for consistency.  
- Regularly review CI configurations for dependency or policy drift.  
- Keep this file synchronized across UIBCDF projects when possible.  

---

## 10. Formatting Tools

- All repositories are formatted and linted with **Ruff**. The canonical configuration lives in `pyproject.toml` under `[tool.ruff]`, `[tool.ruff.lint]`, and `[tool.ruff.format]`.

- Contributors should run:

  ```bash
  ruff format .
  ruff check .
  ```

  before submitting any pull request.

---

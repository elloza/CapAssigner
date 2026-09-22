# Research: Application Scaffolding and Architecture

**Feature**: Application Scaffolding and Architecture
**Date**: 2025-10-20
**Purpose**: Document best practices and technical decisions for project structure setup

---

## 1. Python Project Structure for Scientific Computing

### Decision: Modular package structure with core/ui separation

**Rationale**:
- **Separation of Concerns**: Scientific computation (`core/`) vs presentation (`ui/`) enables independent testing and potential CLI/API reuse
- **Import Control**: Explicit package structure prevents circular dependencies and enforces architectural boundaries
- **Standard Practice**: Follows Python Packaging Authority (PyPA) recommendations for namespace packages

**Alternatives Considered**:
- **Flat structure** (all files in root): Rejected - becomes unmanageable beyond 10-15 files, no clear boundaries
- **Feature-based structure** (by algorithm type): Rejected - breaks modular architecture principle, mixes concerns
- **Monolithic app.py**: Rejected - violates testability, makes refactoring difficult

**References**:
- PyPA Packaging Guide: https://packaging.python.org/
- Scientific Python Development Guide: https://learn.scientific-python.org/development/
- Real Python Project Structure: https://realpython.com/python-application-layouts/

---

## 2. Conda Environment Management

### Decision: Use conda environment at `.conda/` (prefix-based) with pip for package installation

**Rationale**:
- **User Requirement**: Explicitly requested conda environment at `.conda/` in project root
- **Prefix-based Advantage**: Project-local environment travels with repository, no name conflicts
- **Hybrid Approach**: Conda creates base Python environment, pip installs application dependencies
- **Best Practice**: Conda for Python version management, pip for pure-Python packages

**Implementation**:
```bash
# Create environment
conda create --prefix ./.conda python=3.9

# Activate
conda activate ./.conda

# Install dependencies
pip install -r requirements.txt
```

**Alternatives Considered**:
- **Named conda environment** (conda create -n capassigner): Rejected - user specified `.conda/` path
- **Pure pip with venv**: Rejected - user requirement mandates conda
- **Conda-only dependencies**: Rejected - many packages (streamlit, schemdraw) better maintained on PyPI

**Gotchas**:
- `.gitignore` MUST exclude `.conda/` to avoid committing binary files
- `environment.yml` documents the conda environment but uses `--prefix` in creation
- Activation requires full or relative path: `conda activate ./.conda`

**References**:
- Conda User Guide: https://docs.conda.io/projects/conda/en/latest/user-guide/
- Managing environments: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

---

## 3. Linting Tools: Ruff vs Black+Flake8

### Decision: Use Ruff as primary linter

**Rationale**:
- **Performance**: 10-100x faster than flake8, instant feedback
- **All-in-one**: Replaces flake8, isort, pyupgrade, and many flake8 plugins
- **Black compatibility**: Can enforce Black code style with `ruff format` or work alongside Black
- **Actively maintained**: Rust-based, modern Python best practices
- **Constitutional requirement**: Constitution mandates "ruff or black + isort" - ruff is simpler

**Configuration Strategy**:
- Use Ruff for linting (`ruff check`) and auto-fixing (`ruff check --fix`)
- Use Black for formatting (`black .`) for consistency with Streamlit ecosystem
- Use isort for import sorting (`isort .`) with Black profile

**pyproject.toml Example**:
```toml
[tool.ruff]
line-length = 100
target-version = "py39"
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4", "SIM"]
ignore = ["E501"]  # Line too long (handled by black)

[tool.black]
line-length = 100
target-version = ["py39"]

[tool.isort]
profile = "black"
line_length = 100
```

**Alternatives Considered**:
- **Flake8 + plugins**: Rejected - slower, requires multiple tools
- **Pylint**: Rejected - too opinionated, many false positives
- **Ruff format only**: Considered but keeping Black for ecosystem compatibility

**References**:
- Ruff Documentation: https://docs.astral.sh/ruff/
- Black Documentation: https://black.readthedocs.io/

---

## 4. Pytest Configuration Best Practices

### Decision: Use pytest with markers, fixtures, and conftest.py pattern

**Rationale**:
- **Industry Standard**: pytest is de facto standard for Python testing
- **Flexible Architecture**: Supports unit, integration, and contract tests via markers
- **Fixture System**: Enables test setup/teardown without boilerplate
- **Discovery**: Auto-discovers `test_*.py` files, minimal configuration

**Configuration Strategy**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (slower, dependencies)",
    "contract: Contract tests (interface stability)",
]
```

**Directory Structure**:
- `tests/unit/` - Fast, isolated tests (no I/O, mocked dependencies)
- `tests/integration/` - Module interaction tests (real dependencies)
- `tests/contract/` - API/interface stability tests (public contracts)

**Alternatives Considered**:
- **unittest**: Rejected - more boilerplate, less readable
- **nose2**: Rejected - maintenance mode, pytest is successor
- **doctest**: Supplement only - not comprehensive enough

**References**:
- pytest Documentation: https://docs.pytest.org/
- pytest Best Practices: https://docs.pytest.org/en/stable/explanation/goodpractices.html

---

## 5. Mypy Configuration for Gradual Typing

### Decision: Enable strict mode with selective opt-outs for pragmatic balance

**Rationale**:
- **Constitutional Requirement**: All functions MUST have type hints
- **Gradual Typing**: Allow pragmatic exceptions while enforcing type safety
- **IDE Integration**: Enables autocomplete, refactoring, early error detection
- **Modern Python**: Python 3.9+ has excellent built-in type hint support

**Configuration Strategy**:
```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_unimported = false  # Allow imported Any types
no_implicit_optional = true
strict_equality = true
check_untyped_defs = true

[[tool.mypy.overrides]]
module = ["streamlit.*", "matplotlib.*", "schemdraw.*"]
ignore_missing_imports = true  # Third-party packages without stubs
```

**Key Rules**:
- `disallow_untyped_defs = true`: ENFORCES type hints on all functions (constitutional)
- `ignore_missing_imports = true` for third-party: Pragmatic - not all packages have type stubs
- Use `# type: ignore[error-code]` sparingly with justification

**Alternatives Considered**:
- **No type checking**: Rejected - violates constitution
- **Pyright/Pylance**: Considered but mypy has better ecosystem support
- **Fully strict mode**: Too rigid for Streamlit ecosystem

**References**:
- mypy Documentation: https://mypy.readthedocs.io/
- Python Type Hints (PEP 484): https://peps.python.org/pep-0484/

---

## 6. Pre-commit Hook Setup

### Decision: Use pre-commit framework with ruff, black, isort, mypy, and standard hooks

**Rationale**:
- **Automated Quality**: Runs checks before commit, catches issues early
- **Team Consistency**: Same checks for all developers, no manual enforcement
- **Fast Feedback**: Local validation faster than CI pipeline

**Configuration (.pre-commit-config.yaml)**:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Usage**:
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

**Alternatives Considered**:
- **Git hooks manually**: Rejected - hard to maintain, not portable
- **CI-only checks**: Rejected - slower feedback loop
- **Husky (JS tool)**: Rejected - Python ecosystem standard is pre-commit

**References**:
- pre-commit Documentation: https://pre-commit.com/

---

## 7. Cross-platform Path Handling

### Decision: Use pathlib.Path exclusively, avoid os.path

**Rationale**:
- **Constitutional Requirement**: Edge case specifies cross-platform compatibility
- **Modern Standard**: pathlib is Python 3.4+ standard library
- **Object-oriented**: Cleaner API than os.path string manipulation
- **Automatic Separators**: Handles `/` vs `\` transparently

**Best Practices**:
```python
from pathlib import Path

# Good
config_file = Path(__file__).parent / "config.py"
data_dir = Path.cwd() / "data"

# Bad (avoid)
import os
config_file = os.path.join(os.path.dirname(__file__), "config.py")
```

**Key Patterns**:
- `Path.cwd()` - Current working directory
- `Path.home()` - User home directory
- `Path(__file__).parent` - Script directory
- `/` operator for joining paths
- `.resolve()` for absolute paths

**Alternatives Considered**:
- **os.path**: Rejected - older API, string-based, less readable
- **Environment-specific code**: Rejected - pathlib handles this automatically

**References**:
- pathlib Documentation: https://docs.python.org/3/library/pathlib.html

---

## 8. Streamlit Project Structure Patterns

### Decision: Single app.py entry point with modular UI components

**Rationale**:
- **Streamlit Standard**: Official Streamlit apps use single entry point
- **Session State Management**: Centralized in app.py, components are stateless
- **Modular UI**: `ui/` package contains reusable widgets and layouts
- **No Multipage Initially**: Single scaffolding page, multipage for future features

**Pattern**:
```python
# app.py
import streamlit as st
from capassigner.ui.pages import render_main_page

st.set_page_config(
    page_title="CapAssigner",
    page_icon="🔌",
    layout="wide"
)

render_main_page()
```

**Session State Guidelines** (per constitution):
- Use `st.session_state["key"]` for mutable state
- Initialize in app.py before widget calls
- Use unique, stable keys for all widgets
- Avoid global variables

**Alternatives Considered**:
- **Multipage structure** (pages/ directory): Deferred to future features
- **Class-based components**: Rejected - Streamlit is function-oriented
- **Global state**: Rejected - violates constitutional state management requirement

**References**:
- Streamlit Documentation: https://docs.streamlit.io/
- Session State Guide: https://docs.streamlit.io/library/api-reference/session-state

---

## 9. Python 3.9+ Type Hints

### Decision: Use modern type hints with `from __future__ import annotations`

**Rationale**:
- **Constitutional Requirement**: All functions MUST have type hints
- **Python 3.9+**: Target version supports modern syntax
- **PEP 585**: Built-in generics (list[str] vs List[str])
- **PEP 604**: Union operator (str | None vs Optional[str])

**Style Guide**:
```python
from __future__ import annotations  # Enable deferred evaluation

from typing import Callable, Protocol
from collections.abc import Sequence

# Good (modern)
def process_values(
    values: list[float],
    callback: Callable[[int, int], None] | None = None
) -> dict[str, float]:
    ...

# Old style (avoid)
from typing import List, Dict, Optional, Callable
def process_values(
    values: List[float],
    callback: Optional[Callable[[int, int], None]] = None
) -> Dict[str, float]:
    ...
```

**Key Patterns**:
- `list[T]`, `dict[K, V]`, `set[T]` - Built-in generics (PEP 585)
- `X | Y | None` - Union types (PEP 604)
- `Callable[[Args], Return]` - Function types
- `Protocol` - Structural subtyping
- `dataclass` - Data containers with type hints

**Alternatives Considered**:
- **typing module aliases**: Deprecated in Python 3.9+
- **No type hints**: Rejected - constitutional violation
- **Type comments**: Rejected - inline hints are clearer

**References**:
- PEP 585 (Built-in Generics): https://peps.python.org/pep-0585/
- PEP 604 (Union Operator): https://peps.python.org/pep-0604/

---

## 10. Docstring Format: Google Style

### Decision: Use Google-style docstrings for all modules, classes, and functions

**Rationale**:
- **Readability**: More readable than NumPy style, less verbose than Sphinx
- **Streamlit Consistency**: Streamlit itself uses Google style
- **Tool Support**: Sphinx, pydoc, IDEs all support Google format
- **Constitutional Requirement**: All public functions MUST have docstrings

**Template**:
```python
def parse_capacitance(value: str) -> float:
    """Parse capacitance value from string with units.

    Supports multiple formats including scientific notation and unit suffixes
    (pF, nF, µF, uF, mF, F). Case-sensitive for units.

    Args:
        value: String representation of capacitance (e.g., "5.2pF", "1e-11")

    Returns:
        Capacitance value in Farads (float)

    Raises:
        ValueError: If value format is invalid or ambiguous

    Examples:
        >>> parse_capacitance("5.2pF")
        5.2e-12
        >>> parse_capacitance("1e-11")
        1e-11
    """
    ...
```

**Sections**:
- Module: Brief description, usage examples
- Function: Description, Args, Returns, Raises, Examples
- Class: Description, Attributes, Examples

**Alternatives Considered**:
- **NumPy style**: Rejected - more verbose, less familiar to web developers
- **Sphinx reST**: Rejected - harder to read in source code
- **No docstrings**: Rejected - constitutional violation

**References**:
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
- Example Docstrings: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

---

## Summary of Technical Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Project Structure | Modular core/ui separation | Constitutional requirement, testability |
| Environment | Conda at `.conda/` + pip | User requirement, hybrid best practice |
| Linting | Ruff + Black + isort | Speed, simplicity, Black compatibility |
| Testing | pytest with markers | Industry standard, flexible |
| Type Checking | mypy strict mode | Constitutional requirement, IDE support |
| Pre-commit | Standard hooks + quality tools | Automated consistency |
| Paths | pathlib.Path | Cross-platform, modern standard |
| Streamlit | Single entry point, session state | Official pattern, state management |
| Type Hints | Python 3.9+ built-in generics | Modern, readable, less imports |
| Docstrings | Google style | Readable, Streamlit-consistent |

All decisions comply with constitutional requirements and user specifications (conda environment at `.conda/`).

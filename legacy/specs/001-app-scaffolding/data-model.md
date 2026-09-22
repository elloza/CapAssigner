# Data Model: Application Scaffolding and Architecture

**Feature**: Application Scaffolding and Architecture
**Date**: 2025-10-20
**Purpose**: Define the entities and relationships for project structure scaffolding

---

## Overview

This data model describes the **meta-structure** of the CapAssigner project scaffolding - the files, directories, and configurations that make up the project foundation. Unlike typical data models that describe application entities (users, products, etc.), this model describes the scaffolding artifacts themselves.

---

## Entities

### 1. ProjectRoot

**Description**: The top-level directory containing all project files and subdirectories.

**Attributes**:
- `path`: Absolute path to repository root (pathlib.Path)
- `git_initialized`: Whether .git directory exists (bool)
- `conda_env_path`: Path to conda environment (./.conda)

**Relationships**:
- Contains 1 ApplicationPackage (`capassigner/`)
- Contains 1 TestDirectory (`tests/`)
- Contains multiple ConfigurationFiles
- Contains 1 EntryPoint (`app.py`)

**Validation Rules**:
- MUST be a valid directory
- MUST contain `.git/` for version control
- MUST NOT contain `.conda/` in version control (git-ignored)

**State**:
- Initialized → Scaffolded → Configured → Ready

---

### 2. ApplicationPackage

**Description**: The main `capassigner/` Python package containing all application code.

**Attributes**:
- `name`: Package name (str = "capassigner")
- `has_init`: Whether `__init__.py` exists (bool)
- `importable`: Whether package can be imported (bool)

**Relationships**:
- Contains 1 CorePackage (`core/`)
- Contains 1 UIPackage (`ui/`)
- Contains 1 ConfigurationModule (`config.py`)
- Contains 1 `__init__.py` file

**Validation Rules**:
- MUST have `__init__.py` for package discovery
- MUST be importable from Python
- Name MUST match repository structure

---

### 3. CorePackage

**Description**: The `capassigner/core/` subpackage containing pure computation logic (NO Streamlit dependencies).

**Attributes**:
- `name`: Subpackage name (str = "core")
- `has_streamlit_imports`: Whether any module imports streamlit (bool - MUST be False)
- `modules`: List of module files

**Relationships**:
- Contains 6 PlaceholderModules:
  - `parsing.py`
  - `sp_structures.py`
  - `sp_enumeration.py`
  - `graphs.py`
  - `heuristics.py`
  - `metrics.py`
- Contains 1 `__init__.py` file

**Validation Rules** (Constitutional):
- MUST NOT import `streamlit` in any module
- All functions MUST have type hints (PEP 484)
- All functions MUST have Google-style docstrings
- All functions MUST accept optional `progress_cb` parameter for UI updates

---

### 4. UIPackage

**Description**: The `capassigner/ui/` subpackage containing Streamlit-specific presentation code.

**Attributes**:
- `name`: Subpackage name (str = "ui")
- `modules`: List of module files

**Relationships**:
- Contains 4 PlaceholderModules:
  - `pages.py`
  - `theory.py`
  - `plots.py`
  - `tooltips.py`
- Contains 1 `__init__.py` file

**Validation Rules**:
- MAY import from `capassigner.core`
- MAY import `streamlit`
- MUST NOT be imported by `core/` modules (one-way dependency)

---

### 5. PlaceholderModule

**Description**: A Python module file with minimal structure (docstring, type hints, placeholder functions).

**Attributes**:
- `filename`: Module filename (str, e.g., "parsing.py")
- `full_path`: Absolute path (pathlib.Path)
- `package`: Parent package (str, e.g., "capassigner.core")
- `has_docstring`: Module-level docstring present (bool)
- `has_type_hints`: All functions have type hints (bool)
- `importable`: Can be imported without errors (bool)

**Relationships**:
- Belongs to 1 CorePackage or UIPackage
- Contains 0-N functions (initially placeholder)

**Validation Rules**:
- MUST have module-level docstring explaining purpose
- MUST be syntactically valid Python
- MUST be importable (no import errors)
- If in `core/`, MUST NOT import `streamlit`

**Template Structure**:
```python
"""Module purpose and usage description.

This is a placeholder module created during scaffolding.
Implementation details will be added in subsequent features.
"""

from __future__ import annotations
from typing import Any


def placeholder_function() -> None:
    """Placeholder function for future implementation.

    This function will be implemented in a future feature.
    See the project roadmap for details.
    """
    pass
```

---

### 6. ConfigurationModule

**Description**: The `capassigner/config.py` module containing application-wide constants.

**Attributes**:
- `filename`: "config.py"
- `constants`: Dictionary of constant names and values

**Relationships**:
- Referenced by all `core/` and `ui/` modules

**Validation Rules** (Constitutional):
- MUST define `DEFAULT_N_MAX_SP = 8`
- MUST define `DEFAULT_HEURISTIC_ITERS = 2000`
- MUST define `DEFAULT_MAX_INTERNAL = 2`
- MUST define `DEFAULT_SEED = 0`
- All values MUST be immutable (int, float, str, tuple)
- MUST NOT use global mutable state (no lists, dicts)

**Template**:
```python
"""Application configuration constants.

Constitutional defaults for performance and algorithms.
"""

# Performance limits (Principle V: Performance Awareness)
DEFAULT_N_MAX_SP: int = 8  # Max capacitors for SP exhaustive search

# Heuristic defaults
DEFAULT_HEURISTIC_ITERS: int = 2000
DEFAULT_MAX_INTERNAL: int = 2  # Max internal nodes in graph heuristic
DEFAULT_SEED: int = 0  # Random seed for reproducibility

# UI defaults
DEFAULT_TOLERANCE_PERCENT: float = 1.0  # 1% of C_obj
```

---

### 7. TestDirectory

**Description**: The `tests/` directory containing all test files.

**Attributes**:
- `path`: Directory path (pathlib.Path)
- `has_conftest`: Whether conftest.py exists (bool)

**Relationships**:
- Contains 3 TestSubdirectories:
  - `unit/`
  - `integration/`
  - `contract/`
- Contains 1 `conftest.py` file

**Validation Rules**:
- MUST have `__init__.py` in each subdirectory
- MUST have `conftest.py` with pytest configuration
- MUST be discoverable by pytest

---

### 8. TestSubdirectory

**Description**: A subdirectory within `tests/` for a specific test type.

**Attributes**:
- `name`: Subdirectory name (str: "unit", "integration", or "contract")
- `test_files`: List of test_*.py files

**Relationships**:
- Contains 0-N TestFiles (initially empty)
- Belongs to 1 TestDirectory

**Validation Rules**:
- MUST have `__init__.py`
- Test files MUST match pattern `test_*.py`

---

### 9. ConfigurationFile

**Description**: A configuration file for tools or project metadata.

**Attributes**:
- `filename`: File name (str)
- `type`: File type (str: "toml", "yaml", "txt", "md", "ignore")
- `purpose`: What the file configures (str)

**Relationships**:
- Belongs to 1 ProjectRoot

**Instances**:

| Filename | Type | Purpose |
|----------|------|---------|
| `requirements.txt` | txt | pip dependencies |
| `environment.yml` | yaml | Conda environment spec |
| `pyproject.toml` | toml | Tool configuration (ruff, black, isort, pytest, mypy) |
| `.pre-commit-config.yaml` | yaml | Pre-commit hooks |
| `.gitignore` | ignore | Git exclusion patterns |
| `README.md` | md | Project documentation |

**Validation Rules**:
- `requirements.txt` MUST include all mandatory dependencies with version constraints
- `pyproject.toml` MUST configure ruff, black, isort, pytest, mypy
- `.gitignore` MUST exclude `.conda/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- `environment.yml` MUST specify python=3.9

---

### 10. EntryPoint

**Description**: The `app.py` file that launches the Streamlit application.

**Attributes**:
- `filename`: "app.py"
- `has_page_config`: Whether st.set_page_config() is called (bool)
- `imports_ui`: Whether it imports from capassigner.ui (bool)

**Relationships**:
- Belongs to 1 ProjectRoot
- Imports from UIPackage

**Validation Rules**:
- MUST call `st.set_page_config()` before other Streamlit calls
- MUST import from `capassigner.ui` (not inline code)
- MUST be executable with `streamlit run app.py`

**Template**:
```python
"""CapAssigner - Capacitor Network Synthesis Application.

Streamlit entry point for the application.
"""

import streamlit as st
from capassigner.ui.pages import render_placeholder_page


st.set_page_config(
    page_title="CapAssigner",
    page_icon="🔌",
    layout="wide",
)

render_placeholder_page()
```

---

## Entity Relationships Diagram

```
ProjectRoot
├── ApplicationPackage (capassigner/)
│   ├── CorePackage (core/)
│   │   ├── PlaceholderModule (parsing.py)
│   │   ├── PlaceholderModule (sp_structures.py)
│   │   ├── PlaceholderModule (sp_enumeration.py)
│   │   ├── PlaceholderModule (graphs.py)
│   │   ├── PlaceholderModule (heuristics.py)
│   │   └── PlaceholderModule (metrics.py)
│   ├── UIPackage (ui/)
│   │   ├── PlaceholderModule (pages.py)
│   │   ├── PlaceholderModule (theory.py)
│   │   ├── PlaceholderModule (plots.py)
│   │   └── PlaceholderModule (tooltips.py)
│   └── ConfigurationModule (config.py)
├── TestDirectory (tests/)
│   ├── TestSubdirectory (unit/)
│   ├── TestSubdirectory (integration/)
│   └── TestSubdirectory (contract/)
├── EntryPoint (app.py)
└── ConfigurationFiles
    ├── requirements.txt
    ├── environment.yml
    ├── pyproject.toml
    ├── .pre-commit-config.yaml
    ├── .gitignore
    └── README.md
```

---

## Validation Matrix

| Entity | Constitutional Principle | Validation Method |
|--------|-------------------------|-------------------|
| CorePackage | IV. Modular Architecture | grep -r "import streamlit" capassigner/core/ returns empty |
| PlaceholderModule | Dev Standards: Code Quality | mypy --strict passes, all functions have type hints |
| ConfigurationModule | V. Performance Awareness | Contains DEFAULT_N_MAX_SP=8, DEFAULT_HEURISTIC_ITERS=2000 |
| TestDirectory | Quality & Testing | pytest discovers structure, runs without errors |
| ConfigurationFiles | All principles | Tools run successfully (ruff, black, isort, mypy, pytest) |
| EntryPoint | II. User Experience First | streamlit run app.py launches without errors |

---

## State Transitions

### ProjectRoot State Machine

```
[Empty Repo]
    ↓ (Create directories)
[Directories Created]
    ↓ (Create placeholder modules)
[Modules Created]
    ↓ (Create configuration files)
[Configuration Complete]
    ↓ (Install dependencies)
[Dependencies Installed]
    ↓ (Run validation)
[Ready for Development] ✅
```

### PlaceholderModule State Machine

```
[Not Exists]
    ↓ (Create file with template)
[Template Created]
    ↓ (Add docstrings)
[Documented]
    ↓ (Add type hints)
[Typed]
    ↓ (Test import)
[Importable] ✅
```

---

## Implementation Order

To satisfy dependencies, entities must be created in this order:

1. **ProjectRoot** - Verify directory exists
2. **ApplicationPackage** - Create `capassigner/` and `capassigner/__init__.py`
3. **CorePackage** - Create `capassigner/core/` and `__init__.py`
4. **UIPackage** - Create `capassigner/ui/` and `__init__.py`
5. **PlaceholderModules** - Create all 10 modules (6 core + 4 ui)
6. **ConfigurationModule** - Create `capassigner/config.py` with constants
7. **TestDirectory** - Create `tests/` and subdirectories
8. **ConfigurationFiles** - Create all 6 config files
9. **EntryPoint** - Create `app.py`
10. **Validation** - Run all validation checks

---

## Notes

- This is a **meta-data model** - it describes the project structure itself, not application domain data
- All paths use `pathlib.Path` for cross-platform compatibility
- Validation rules enforce constitutional requirements
- State transitions ensure proper initialization order
- Template structures ensure consistency across all placeholder modules

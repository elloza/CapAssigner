# Implementation Plan: Application Scaffolding and Architecture

**Branch**: `001-app-scaffolding` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-app-scaffolding/spec.md`

**Note**: This plan establishes the foundational project structure for CapAssigner, a Streamlit-based capacitor network synthesis application.

## Summary

This feature creates the complete scaffolding and architecture for the CapAssigner application, including modular directory structure (`capassigner/core/`, `capassigner/ui/`, `tests/`), dependency configuration, code quality tooling, and documentation. The implementation follows the constitutional principle of Modular Architecture with strict separation between pure computation (core) and UI presentation layers. The scaffolding enables immediate development with proper type hints, testing infrastructure, and best practices from day one.

## Technical Context

**Language/Version**: Python 3.9+ (requires modern type hints, pathlib, dataclasses)
**Primary Dependencies**: Streamlit (UI framework), NumPy (numerical operations), Pandas (data handling), Matplotlib (plotting), NetworkX (graph visualization), SchemDraw (circuit diagrams)
**Storage**: File-based only (no database) - configuration in `config.py`, user data in session state
**Testing**: pytest (test framework), mypy (type checking), ruff (linting), black (formatting), isort (import sorting)
**Target Platform**: Cross-platform (Windows, Linux, macOS) - web application accessed via browser
**Project Type**: Single-project Streamlit application with modular package structure
**Environment Manager**: Conda environment at `.conda/` in project root (user requirement)
**Performance Goals**: <5 minutes from clone to running app, zero linting errors on scaffolding, <10 minutes for new developer onboarding
**Constraints**: Cross-platform compatibility required, Python 3.9+ minimum, no external database dependencies
**Scale/Scope**: Single-user desktop application, 6 core modules + 4 UI modules + config + tests, ~15-20 initial files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle IV: Modular Architecture ✅ COMPLIANT

**Requirements**:
- `core/` modules MUST NOT import `streamlit` ✅ Enforced by structure
- `core/` functions MUST accept `progress_cb` optional parameter ✅ Will be in module templates
- ALL `core/` functions MUST have type hints (PEP 484) and docstrings ✅ Enforced by mypy config
- `ui/` modules MAY import from `core/` but not vice versa ✅ Enforced by import structure

**Verification**: Project structure explicitly separates `capassigner/core/` (computation) from `capassigner/ui/` (presentation). Module templates will include proper type hints and docstrings.

### Development Standards: Code Quality ✅ COMPLIANT

**Requirements**:
- **Type hints**: All functions MUST have PEP 484 type annotations ✅ mypy configured
- **Docstrings**: All public functions MUST have Google or NumPy style docstrings ✅ Template enforced
- **Linting**: Use `ruff` or `black` + `isort` for consistent formatting ✅ pyproject.toml configured
- **Pre-commit hooks**: Configure for linting and type checking ✅ .pre-commit-config.yaml included

**Verification**: FR-008 mandates configuration files for all code quality tools.

### Development Standards: State Management ✅ COMPLIANT

**Requirements**:
- **Session state**: Use `st.session_state` for editable tables, method selection, parameters ✅ Documented in quickstart
- **Unique keys**: ALL widgets MUST have unique, stable keys ✅ Will be in UI module guidelines
- **No global mutable state**: Avoid globals; prefer function parameters or session state ✅ Enforced by structure

**Verification**: `config.py` contains only immutable constants, all mutable state in Streamlit session.

### Quality & Testing: Test Coverage ✅ COMPLIANT

**Requirements**:
- Test structure with `unit/`, `integration/`, `contract/` directories ✅ FR-005
- pytest configuration ✅ FR-008, pyproject.toml
- Placeholder tests that pass ✅ Will be generated

**Verification**: FR-005 mandates test directory structure with subdirectories.

### User Input Requirement: Conda Environment ✅ COMPLIANT

**Requirements**:
- MUST use Conda environment at `.conda/` in project root
- Documentation MUST reference conda activation
- Setup instructions MUST use conda commands

**Verification**: README and quickstart.md will document conda environment setup. `.gitignore` will exclude `.conda/` directory.

**GATE RESULT**: ✅ **PASS** - All constitutional requirements met. No violations to justify.

## Project Structure

### Documentation (this feature)

```
specs/001-app-scaffolding/
├── plan.md              # This file (implementation plan)
├── research.md          # Best practices for Python project structure, linting tools, conda setup
├── data-model.md        # Project structure entity model
├── quickstart.md        # Developer onboarding guide
├── contracts/           # N/A for scaffolding (no APIs)
└── checklists/
    └── requirements.md  # Spec quality validation checklist
```

### Source Code (repository root)

```
CapAssigner/
├── .conda/                     # Conda environment (user-specified, git-ignored)
├── capassigner/                # Main application package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Application constants and configuration
│   ├── core/                  # Pure computation (NO streamlit imports)
│   │   ├── __init__.py
│   │   ├── parsing.py         # Capacitance value parsing (pF, nF, µF, scientific notation)
│   │   ├── sp_structures.py   # Series-Parallel data types (Leaf, Series, Parallel)
│   │   ├── sp_enumeration.py  # SP topology enumeration algorithms
│   │   ├── graphs.py          # Graph-based network analysis (Laplacian)
│   │   ├── heuristics.py      # Advanced search methods (GA/SA/PSO - future)
│   │   └── metrics.py         # Error calculations (abs, rel, tolerance checks)
│   └── ui/                    # Streamlit-specific presentation
│       ├── __init__.py
│       ├── pages.py           # Main UI layout and widgets
│       ├── theory.py          # Educational content (formulas, explanations)
│       ├── plots.py           # Visualization (SchemDraw, NetworkX)
│       └── tooltips.py        # Help text for all widgets
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py            # pytest configuration and fixtures
│   ├── unit/                  # Unit tests (individual functions)
│   │   └── __init__.py
│   ├── integration/           # Integration tests (module interactions)
│   │   └── __init__.py
│   └── contract/              # Contract tests (API/interface stability)
│       └── __init__.py
├── app.py                     # Streamlit entry point
├── requirements.txt           # pip dependencies
├── environment.yml            # Conda environment specification (user requirement)
├── pyproject.toml             # Tool configuration (ruff, black, isort, pytest, mypy)
├── .pre-commit-config.yaml    # Pre-commit hooks for code quality
├── .gitignore                 # Git exclusions (.conda/, __pycache__, .pytest_cache, etc.)
└── README.md                  # Project documentation with conda setup instructions
```

**Structure Decision**: Single-project layout selected because:
1. CapAssigner is a monolithic Streamlit application (not separate frontend/backend)
2. No API server or mobile components
3. All functionality served through single Streamlit instance
4. Modular architecture achieved through package separation (`core/` vs `ui/`)
5. Follows constitutional Principle IV (Modular Architecture) exactly as specified

**Conda Environment**: Per user requirement, the project MUST use a conda environment located at `.conda/` in the project root. This will be documented in README.md and quickstart.md with activation instructions.

## Complexity Tracking

*No constitutional violations - this section is empty.*

---

## Phase 0: Research & Best Practices

**Status**: ✅ **COMPLETE** - See [research.md](./research.md)

**Key Decisions**:
1. ✅ Modular package structure with core/ui separation
2. ✅ Conda environment at `.conda/` with pip for packages
3. ✅ Ruff as primary linter (chosen for speed and simplicity)
4. ✅ pytest with markers for test categories (unit, integration, contract)
5. ✅ mypy strict mode with selective opt-outs
6. ✅ pre-commit hooks for automated quality checks
7. ✅ pathlib.Path for cross-platform compatibility
8. ✅ Single entry point pattern for Streamlit
9. ✅ Python 3.9+ built-in generics (list[T], X | Y)
10. ✅ Google-style docstrings

**Deliverables**:
- ✅ [research.md](./research.md) - Comprehensive best practices documentation with rationale

---

## Phase 1: Design Artifacts

**Status**: ✅ **COMPLETE**

**Deliverables**:
- ✅ [data-model.md](./data-model.md) - Project structure entity model (10 entities with validation rules)
- ✅ [quickstart.md](./quickstart.md) - Developer onboarding guide (<10 minute setup)
- ✅ [CLAUDE.md](../../CLAUDE.md) - Agent context updated with tech stack
- ⚠️ contracts/ - N/A (scaffolding has no API contracts)

---

## Implementation Notes

### Conda Environment Setup

Per user requirement, developers MUST use conda environment at `.conda/`:

```bash
# Create conda environment
conda create --prefix ./.conda python=3.9

# Activate
conda activate ./.conda

# Install dependencies
pip install -r requirements.txt
```

### Key Files to Generate

1. **requirements.txt**: Pin major versions, allow patch updates
   - streamlit>=1.28.0,<2.0.0
   - numpy>=1.24.0,<2.0.0
   - pandas>=2.0.0,<3.0.0
   - matplotlib>=3.7.0,<4.0.0
   - networkx>=3.1.0,<4.0.0
   - schemdraw>=0.16.0,<1.0.0
   - Optional: scipy>=1.11.0, numba>=0.57.0

2. **environment.yml**: Conda environment specification
   - name: capassigner
   - python=3.9
   - pip dependencies from requirements.txt

3. **pyproject.toml**: Unified tool configuration
   - [tool.ruff]: Select rules, line length 100
   - [tool.black]: Line length 100, target Python 3.9
   - [tool.isort]: Profile "black"
   - [tool.pytest.ini_options]: Test discovery patterns, markers
   - [tool.mypy]: Strict mode with gradual typing allowances

4. **.pre-commit-config.yaml**: Automated checks
   - ruff (linting)
   - black (formatting)
   - isort (import sorting)
   - mypy (type checking)
   - trailing-whitespace, end-of-file-fixer

5. **Module templates**: Each placeholder module includes:
   - Module-level docstring (purpose, usage)
   - Type hints on all functions
   - Google-style docstrings
   - `progress_cb` parameter for core modules

### Validation Steps

Before marking this feature complete:
1. ✅ All directories exist per structure above
2. ✅ `conda activate ./.conda && pip install -r requirements.txt` succeeds
3. ✅ `streamlit run app.py` launches placeholder page
4. ✅ `ruff check capassigner/` passes (zero errors)
5. ✅ `black --check capassigner/` passes
6. ✅ `isort --check capassigner/` passes
7. ✅ `mypy capassigner/` passes
8. ✅ `pytest` discovers structure, reports zero errors
9. ✅ `python -c "import capassigner.core; import capassigner.ui"` succeeds
10. ✅ All `.gitignore` patterns exclude `.conda/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`

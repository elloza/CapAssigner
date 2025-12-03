# Implementation Plan: Complete CapAssigner Application

**Branch**: `002-full-app-implementation` | **Date**: 2025-10-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-full-app-implementation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a complete web-based capacitor network synthesis application that finds optimal series-parallel and general graph topologies to achieve target capacitance values. The application provides two primary methods: (1) exhaustive series-parallel enumeration using dynamic programming for small networks (N≤8), and (2) heuristic graph search with Laplacian-based nodal analysis for larger networks or non-SP topologies. Key features include flexible input parsing (unit suffixes, scientific notation), visual circuit diagrams (SchemDraw for SP, NetworkX for graphs), error metric calculations, tolerance checking, progress feedback, and educational theory explanations.

## Technical Context

**Language/Version**: Python 3.9+ (requires modern type hints per PEP 484, 585, 604; pathlib; dataclasses)
**Primary Dependencies**: Streamlit (UI framework), NumPy (numerical operations, matrix solving), Pandas (data handling for results tables), Matplotlib (plotting), NetworkX (graph visualization and topology representation), SchemDraw (circuit diagram rendering)
**Storage**: Session state only (st.session_state); no persistent database required for MVP
**Testing**: pytest with coverage for parsing, SP enumeration, graph C_eq calculation, and stability tests
**Target Platform**: Web application (Streamlit), deployable to Streamlit Cloud or local execution; modern browsers (Chrome, Firefox, Edge, Safari)
**Project Type**: Single web application with modular architecture (core/ and ui/ separation)
**Performance Goals**: SP solutions for N=5 in <3 seconds; heuristic search (2000 iterations) in <10 seconds; operations >1s show progress feedback
**Constraints**: SP exhaustive limited to N≤8 due to Catalan(N)×N! complexity; heuristic search practical up to ~20 capacitors; double precision (IEEE 754) sufficient
**Scale/Scope**: MVP targets engineering students and practicing engineers; single-user sessions; typical workflows complete in <2 minutes; ~10 core modules + ~5 UI modules + comprehensive test suite

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Applicable Principles

**I. Scientific Accuracy** ✓ APPLIES
This feature implements all core circuit theory formulas:
- Parallel: C_p = Σ C_i (FR-001)
- Series: 1/C_s = Σ (1/C_i) (FR-002)
- Laplacian nodal analysis: Y = s·C with V_a=1, V_b=0 (FR-003, FR-004)
- Singular matrix handling (FR-005), disconnected network detection (FR-006), floating node handling (FR-007)

**Compliance Plan**: All formulas will be implemented in `capassigner/core/sp_structures.py` (series/parallel) and `capassigner/core/graphs.py` (Laplacian). Test coverage in `tests/test_sp_smallN.py` and `tests/test_graph_ceq.py` will verify against known results.

---

**II. User Experience First** ✓ APPLIES
This feature requires excellent UX across all interactions:
- Progress bars for operations >1s (FR-034)
- Warning for N>8 in SP exhaustive (FR-035)
- Tooltips for all inputs (FR-042)
- Actionable error messages (FR-011, FR-038)
- Visual diagrams with labeled components (FR-036, FR-037, FR-038, FR-039)

**Compliance Plan**: All progress callbacks will be implemented in core functions with optional `progress_cb` parameter. UI modules in `capassigner/ui/` will wire these to Streamlit progress bars. Tooltips defined in `capassigner/ui/tooltips.py`. Error messages will show problematic input and expected format.

---

**III. Robust Input Handling** ✓ APPLIES
This feature implements comprehensive parsing:
- Unit suffixes: pF, nF, µF, uF, mF, F (FR-008)
- Scientific notation: 1e-11, 1*10^-11, etc. (FR-009)
- Plain decimals (FR-010)
- Clear error messages with format examples (FR-011)
- Human-readable output formatting (FR-012)

**Compliance Plan**: All parsing logic in `capassigner/core/parsing.py`. Test coverage in `tests/test_parsing.py` for all formats plus edge cases (negative, zero, invalid).

---

**IV. Modular Architecture** ✓ APPLIES
This feature extends the existing modular structure:
- `core/` modules have NO Streamlit imports (verified in scaffolding)
- All `core/` functions have type hints and docstrings
- All `core/` functions accept optional `progress_cb` parameter
- `ui/` modules import from `core/` but not vice versa

**Compliance Plan**: Architecture already established in 001-app-scaffolding. This feature fills in placeholder implementations while maintaining separation. Pre-commit hooks enforce linting and type checking.

---

**V. Performance Awareness** ✓ APPLIES
This feature respects computational complexity:
- SP exhaustive limited to N≤8 (FR-017), configurable in `config.py`
- Warning shown when N>8 selected (FR-035)
- Heuristic defaults documented (FR-019, FR-020, FR-021)
- Caching with `@st.cache_data` for stable inputs (FR-044)

**Compliance Plan**: Default limit `MAX_SP_EXHAUSTIVE_N = 8` in `config.py`. UI will check inventory size and show warning. Heuristic parameters exposed in UI with tooltips explaining defaults.

---

**VI. Educational Transparency** ✓ APPLIES
This feature provides comprehensive educational content:
- Theory sections for each method (FR-040)
- LaTeX-rendered formulas (FR-041)
- Labeled diagrams (FR-038, FR-039)
- Error metric displays (FR-023, FR-024, FR-026)

**Compliance Plan**: Theory content in `capassigner/ui/theory.py` with expanders showing explanations, formulas (using `st.latex`), and usage guidance. Diagrams in `capassigner/ui/plots.py` will annotate all components and terminals.

---

### Gate Results

**Status**: ✅ PASS (initial check)

All six constitutional principles apply to this feature and are addressed in the requirements. No violations or unjustified complexity.

**Post-Design Re-check**: Required after Phase 1 (data-model.md and contracts/) are complete to verify design maintains compliance.

### Post-Design Re-Evaluation (Phase 1 Complete)

**Date**: 2025-10-20
**Artifacts Reviewed**: data-model.md, contracts/ (parsing.yaml, sp_structures.yaml, sp_enumeration.yaml, graphs.yaml, heuristics.yaml, metrics.yaml), quickstart.md

**Principle I: Scientific Accuracy** ✅ COMPLIANT
- Contracts specify exact formulas: C_p = Σ C_i (contracts/sp_structures.yaml), 1/C_s = Σ (1/C_i) (contracts/sp_structures.yaml)
- Laplacian method detailed in contracts/graphs.yaml with boundary conditions V_a=1, V_b=0
- Singular matrix handling specified (pseudo-inverse, regularization)
- Disconnected network detection specified (return C_eq=0)

**Principle II: User Experience First** ✅ COMPLIANT
- ProgressCallback type defined in contracts (sp_enumeration.yaml, heuristics.yaml)
- Progress updates specified every 50 iterations
- Tooltips and error messages documented in contracts and quickstart
- Actionable error messages specified (e.g., "Invalid format '5pf' — use '5pF' with capital F")

**Principle III: Robust Input Handling** ✅ COMPLIANT
- ParsedCapacitance type in contracts/parsing.yaml handles all formats
- Validation rules specified in data-model.md for all entities
- Error handling for invalid inputs detailed in contracts

**Principle IV: Modular Architecture** ✅ COMPLIANT
- Data model maintains separation: SPNode and GraphTopology in core/
- Contracts specify no Streamlit imports in core/ modules
- ProgressCallback pattern maintains separation while enabling UI updates

**Principle V: Performance Awareness** ✅ COMPLIANT
- Performance goals documented in contracts (N=5 <1s, N=8 ~3s, heuristic 2000 iters ~5-10s)
- Memoization specified in sp_enumeration.yaml
- Warning for N>8 documented in quickstart

**Principle VI: Educational Transparency** ✅ COMPLIANT
- Theory sections documented in quickstart.md
- Formulas and explanations specified
- Method comparison provided

**Status**: ✅ PASS (post-design re-check)

All constitutional principles remain satisfied after Phase 1 design. No violations introduced.

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
capassigner/                 # Main package (established in 001-app-scaffolding)
├── __init__.py             # Package initialization
├── config.py               # Constants and configuration (MAX_SP_EXHAUSTIVE_N, etc.)
├── core/                   # Pure computation (NO Streamlit dependencies)
│   ├── __init__.py
│   ├── parsing.py          # Input parsing and formatting (FR-008 to FR-012)
│   ├── sp_structures.py    # Series-parallel data types and formulas (FR-001, FR-002)
│   ├── sp_enumeration.py   # SP exhaustive algorithm (FR-013 to FR-017)
│   ├── graphs.py           # Graph topology and Laplacian analysis (FR-003 to FR-007)
│   ├── heuristics.py       # Random graph generation (FR-018 to FR-022)
│   └── metrics.py          # Error calculations (FR-023 to FR-027)
└── ui/                     # Streamlit-specific presentation
    ├── __init__.py
    ├── pages.py            # Main layout and widget logic (FR-028 to FR-049)
    ├── theory.py           # Educational content and LaTeX formulas (FR-040, FR-041)
    ├── plots.py            # SchemDraw and NetworkX visualizations (FR-036 to FR-039)
    └── tooltips.py         # Help text constants (FR-042)

tests/                      # Test suite (pytest)
├── __init__.py
├── unit/                   # Unit tests for core modules
│   ├── test_parsing.py     # All format variants + edge cases
│   ├── test_sp_structures.py # Series/parallel formula verification
│   ├── test_sp_enumeration.py # SP algorithm correctness
│   ├── test_graphs.py      # Laplacian method correctness
│   ├── test_heuristics.py  # Determinism and parameter handling
│   └── test_metrics.py     # Error calculation edge cases
├── integration/            # Integration tests
│   └── test_workflows.py   # End-to-end user scenarios from spec
└── contract/               # Contract tests (if API exposed in future)
    └── (placeholder)

app.py                      # Streamlit entry point (main application)
requirements.txt            # Pip dependencies
environment.yml             # Conda dependencies
pyproject.toml              # Build configuration
.pre-commit-config.yaml     # Pre-commit hooks (ruff, black, isort, mypy)
```

**Structure Decision**: Single web application with modular architecture. This structure was established in feature 001-app-scaffolding and follows Constitutional Principle IV (Modular Architecture). The core/ui separation enables independent testing of algorithms and prevents tight coupling between business logic and presentation. The current feature (002) will fill in the placeholder implementations created during scaffolding.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**Status**: No violations. Constitution Check passed without exceptions.

The modular architecture (6 core modules + 4 UI modules) is justified by the constitutional requirement for separation of concerns and aligns with the feature's functional scope (6 user stories with distinct algorithmic and UI requirements).


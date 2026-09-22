# Tasks: Application Scaffolding and Architecture

**Input**: Design documents from `/specs/001-app-scaffolding/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: No test tasks included - tests not requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: Root-level `capassigner/`, `tests/`, `app.py`
- Paths use absolute Windows paths with `I:\PROYECTOSVSCODE\CapAssigner\` prefix

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify repository readiness and create foundational directory structure

- [ ] T001 Verify repository root exists at I:\PROYECTOSVSCODE\CapAssigner\ and .git directory is present
- [ ] T002 Create main application package directory at I:\PROYECTOSVSCODE\CapAssigner\capassigner\

**Checkpoint**: Repository verified, root package directory created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core package structure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 [P] Create core package directory at I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\
- [ ] T004 [P] Create ui package directory at I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\
- [ ] T005 [P] Create tests directory at I:\PROYECTOSVSCODE\CapAssigner\tests\

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Project Structure Creation (Priority: P1) 🎯 MVP

**Goal**: Create well-organized directory structure that separates core computation logic from UI presentation, enabling maintainable and testable capacitor network synthesis algorithms.

**Independent Test**: Verify all required directories exist with placeholder files, and structure matches constitutional requirements for modular architecture (core/ has no streamlit imports).

### Implementation for User Story 1

**Step 1: Core Package Modules (can run in parallel)**

- [ ] T006 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\parsing.py with module docstring, type hints, and placeholder for capacitance value parsing (pF, nF, µF, scientific notation)
- [ ] T007 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\sp_structures.py with module docstring, type hints, and placeholder for Series-Parallel data types (Leaf, Series, Parallel)
- [ ] T008 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\sp_enumeration.py with module docstring, type hints, and placeholder for SP topology enumeration algorithms
- [ ] T009 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\graphs.py with module docstring, type hints, and placeholder for graph-based network analysis (Laplacian)
- [ ] T010 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\heuristics.py with module docstring, type hints, and placeholder for advanced search methods (GA/SA/PSO - future)
- [ ] T011 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\metrics.py with module docstring, type hints, and placeholder for error calculations (abs, rel, tolerance checks)

**Step 2: UI Package Modules (can run in parallel)**

- [ ] T012 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\pages.py with module docstring and placeholder function render_placeholder_page() for main UI layout and widgets
- [ ] T013 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\theory.py with module docstring and placeholder for educational content (formulas, explanations)
- [ ] T014 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\plots.py with module docstring and placeholder for visualization (SchemDraw, NetworkX)
- [ ] T015 [P] [US1] Create placeholder module I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\tooltips.py with module docstring and placeholder for help text for all widgets

**Step 3: Test Directory Structure (can run in parallel)**

- [ ] T016 [P] [US1] Create tests subdirectory I:\PROYECTOSVSCODE\CapAssigner\tests\unit\ for fast, isolated tests
- [ ] T017 [P] [US1] Create tests subdirectory I:\PROYECTOSVSCODE\CapAssigner\tests\integration\ for module interaction tests
- [ ] T018 [P] [US1] Create tests subdirectory I:\PROYECTOSVSCODE\CapAssigner\tests\contract\ for API/interface stability tests
- [ ] T019 [P] [US1] Create empty __init__.py file at I:\PROYECTOSVSCODE\CapAssigner\tests\__init__.py
- [ ] T020 [P] [US1] Create empty __init__.py file at I:\PROYECTOSVSCODE\CapAssigner\tests\unit\__init__.py
- [ ] T021 [P] [US1] Create empty __init__.py file at I:\PROYECTOSVSCODE\CapAssigner\tests\integration\__init__.py
- [ ] T022 [P] [US1] Create empty __init__.py file at I:\PROYECTOSVSCODE\CapAssigner\tests\contract\__init__.py
- [ ] T023 [US1] Create pytest configuration file I:\PROYECTOSVSCODE\CapAssigner\tests\conftest.py with basic fixtures and test setup

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Directory structure complete with all placeholder modules and test directories.

---

## Phase 4: User Story 2 - Dependency Configuration (Priority: P1)

**Goal**: Provide properly configured dependency files enabling developers to install the project and start development immediately.

**Independent Test**: Run `conda activate ./.conda && pip install -r requirements.txt && streamlit run app.py` in fresh environment and verify application launches with placeholder content.

### Implementation for User Story 2

- [ ] T024 [P] [US2] Create requirements.txt at I:\PROYECTOSVSCODE\CapAssigner\requirements.txt with mandatory dependencies: streamlit>=1.28.0,<2.0.0, numpy>=1.24.0,<2.0.0, pandas>=2.0.0,<3.0.0, matplotlib>=3.7.0,<4.0.0, networkx>=3.1.0,<4.0.0, schemdraw>=0.16.0,<1.0.0, and development tools (pytest, mypy, ruff, black, isort, pre-commit)
- [ ] T025 [P] [US2] Create environment.yml at I:\PROYECTOSVSCODE\CapAssigner\environment.yml with conda environment specification (name: capassigner, python=3.9, pip dependencies)
- [ ] T026 [US2] Create Streamlit entry point I:\PROYECTOSVSCODE\CapAssigner\app.py that calls st.set_page_config() with page_title="CapAssigner", page_icon="🔌", layout="wide" and imports render_placeholder_page from capassigner.ui.pages
- [ ] T027 [US2] Update I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\pages.py to implement render_placeholder_page() function that displays welcome message "Welcome to CapAssigner - Capacitor Network Synthesis" with st.title() and st.write()

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Developers can install dependencies and run the application.

---

## Phase 5: User Story 3 - Project Configuration Files (Priority: P2)

**Goal**: Provide configuration files for linting and formatting tools enabling the codebase to maintain consistent style and quality standards from the start.

**Independent Test**: Run `ruff check capassigner/`, `black --check capassigner/`, `isort --check capassigner/`, `mypy capassigner/`, and `pytest` on the project structure and verify all pass with zero errors.

### Implementation for User Story 3

- [ ] T028 [P] [US3] Create pyproject.toml at I:\PROYECTOSVSCODE\CapAssigner\pyproject.toml with [tool.ruff] section (line-length=100, target-version="py39", select rules E/F/W/I/N/UP/B/A/C4/SIM)
- [ ] T029 [P] [US3] Add [tool.black] section to I:\PROYECTOSVSCODE\CapAssigner\pyproject.toml (line-length=100, target-version=["py39"])
- [ ] T030 [P] [US3] Add [tool.isort] section to I:\PROYECTOSVSCODE\CapAssigner\pyproject.toml (profile="black", line_length=100)
- [ ] T031 [P] [US3] Add [tool.pytest.ini_options] section to I:\PROYECTOSVSCODE\CapAssigner\pyproject.toml (testpaths=["tests"], markers for unit/integration/contract)
- [ ] T032 [P] [US3] Add [tool.mypy] section to I:\PROYECTOSVSCODE\CapAssigner\pyproject.toml (python_version="3.9", disallow_untyped_defs=true, warn_return_any=true, ignore_missing_imports for third-party modules)
- [ ] T033 [P] [US3] Create .pre-commit-config.yaml at I:\PROYECTOSVSCODE\CapAssigner\.pre-commit-config.yaml with hooks for ruff, black, isort, mypy, trailing-whitespace, end-of-file-fixer, check-yaml
- [ ] T034 [P] [US3] Create .gitignore at I:\PROYECTOSVSCODE\CapAssigner\.gitignore that excludes .conda/, __pycache__/, .pytest_cache/, .mypy_cache/, *.pyc, *.pyo, *.egg-info/, dist/, build/, .venv/
- [ ] T035 [US3] Create README.md at I:\PROYECTOSVSCODE\CapAssigner\README.md with project title, description, conda environment setup instructions (conda create --prefix ./.conda python=3.9), installation (pip install -r requirements.txt), and running instructions (streamlit run app.py)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. All code quality tools configured and passing.

---

## Phase 6: User Story 4 - Module Initialization and Imports (Priority: P2)

**Goal**: Provide properly configured __init__.py files and config module enabling modules to import from each other correctly and IDE autocomplete to work.

**Independent Test**: Run `python -c "import capassigner.core"`, `python -c "import capassigner.ui"`, `mypy capassigner/`, and verify all succeed without errors. Import capassigner.config and verify constants are accessible.

### Implementation for User Story 4

**Step 1: Package Initialization Files (can run in parallel)**

- [ ] T036 [P] [US4] Create I:\PROYECTOSVSCODE\CapAssigner\capassigner\__init__.py with module docstring "CapAssigner - Capacitor Network Synthesis Application" and __version__ = "0.1.0"
- [ ] T037 [P] [US4] Create I:\PROYECTOSVSCODE\CapAssigner\capassigner\core\__init__.py with module docstring "Core computation modules (NO Streamlit dependencies)" and note about constitutional compliance
- [ ] T038 [P] [US4] Create I:\PROYECTOSVSCODE\CapAssigner\capassigner\ui\__init__.py with module docstring "Streamlit UI presentation modules"

**Step 2: Configuration Module**

- [ ] T039 [US4] Create I:\PROYECTOSVSCODE\CapAssigner\capassigner\config.py with constitutional constants: DEFAULT_N_MAX_SP=8, DEFAULT_HEURISTIC_ITERS=2000, DEFAULT_MAX_INTERNAL=2, DEFAULT_SEED=0, DEFAULT_TOLERANCE_PERCENT=1.0, with Google-style docstrings and type hints

**Step 3: Ensure All Placeholder Modules Follow Template (sequential verification)**

- [ ] T040 [US4] Verify all core modules (T006-T011) include "from __future__ import annotations" and "from typing import Any" imports, have progress_cb parameter in placeholder functions with type hint Callable[[int, int], None] | None = None
- [ ] T041 [US4] Verify all ui modules (T012-T015) follow Google-style docstring format and have type hints on all functions
- [ ] T042 [US4] Run constitutional compliance check: grep -r "import streamlit" capassigner/core/ returns empty (MUST pass)

**Checkpoint**: All user stories should now be independently functional. Project is fully scaffolded and ready for feature development.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation improvements that affect the entire project

- [ ] T043 [P] Run all validation checks from plan.md: all directories exist, conda environment setup works, streamlit launches, all linting tools pass (ruff, black, isort, mypy, pytest)
- [ ] T044 [P] Update README.md with architecture diagram showing capassigner/core/ (6 modules) and capassigner/ui/ (4 modules) separation
- [ ] T045 [P] Add CONTRIBUTING.md at I:\PROYECTOSVSCODE\CapAssigner\CONTRIBUTING.md with development workflow (conda activation, pre-commit hooks, code quality standards)
- [ ] T046 Verify quickstart.md instructions work end-to-end: fresh conda environment → dependencies installed → app runs → quality tools pass
- [ ] T047 Create initial git commit with message "feat: add application scaffolding and architecture\n\nImplement modular project structure with core/ui separation per constitution.\nIncludes all dependencies, code quality tools, and placeholder modules.\n\n🤖 Generated with Claude Code\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

**Checkpoint**: Project scaffolding complete, all validation passing, ready for handoff to feature development.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational (Phase 2) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 7)**: Depends on all user stories (Phases 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Creates directory structure and placeholder modules
- **User Story 2 (P1)**: Can start after US1 (Phase 3) - Requires placeholder modules from US1, specifically ui/pages.py for render_placeholder_page()
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2, but practically benefits from having structure in place
- **User Story 4 (P2)**: MUST start after US1 (Phase 3) - Requires all modules from US1 to exist before adding __init__.py files and verifying imports

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 6 (US4) → Phase 7 (Polish)

**US3 can run in parallel** with US2 and US4 as it's independent.

### Within Each User Story

- **US1**: Steps 1, 2, 3 can all run in parallel (different files, no dependencies)
- **US2**: T024-T025 parallel, then T026, then T027 (depends on T026 creating app.py)
- **US3**: T028-T034 all parallel, then T035 (README benefits from knowing all configs)
- **US4**: Step 1 parallel, then T039, then Step 3 (verification after all files exist)

### Parallel Opportunities

- **Phase 1**: Both tasks can run in parallel if multi-threaded
- **Phase 2**: All three tasks (T003, T004, T005) can run in parallel
- **Phase 3 (US1)**:
  - Step 1: T006-T011 (6 core modules) all parallel
  - Step 2: T012-T015 (4 ui modules) all parallel
  - Step 3: T016-T022 (7 test directory tasks) all parallel
- **Phase 4 (US2)**: T024-T025 parallel
- **Phase 5 (US3)**: T028-T034 (7 config tasks) all parallel
- **Phase 6 (US4)**: T036-T038 (3 __init__.py files) all parallel
- **Phase 7**: T043-T045 (3 validation tasks) all parallel

---

## Parallel Example: User Story 1 (Project Structure)

```bash
# Launch all core modules together:
Task: "Create placeholder module capassigner/core/parsing.py"
Task: "Create placeholder module capassigner/core/sp_structures.py"
Task: "Create placeholder module capassigner/core/sp_enumeration.py"
Task: "Create placeholder module capassigner/core/graphs.py"
Task: "Create placeholder module capassigner/core/heuristics.py"
Task: "Create placeholder module capassigner/core/metrics.py"

# Launch all ui modules together:
Task: "Create placeholder module capassigner/ui/pages.py"
Task: "Create placeholder module capassigner/ui/theory.py"
Task: "Create placeholder module capassigner/ui/plots.py"
Task: "Create placeholder module capassigner/ui/tooltips.py"

# Launch all test directory setup together:
Task: "Create tests/unit/ subdirectory"
Task: "Create tests/integration/ subdirectory"
Task: "Create tests/contract/ subdirectory"
Task: "Create all __init__.py files in tests/"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T005) - CRITICAL
3. Complete Phase 3: User Story 1 (T006-T023) - Directory structure
4. Complete Phase 4: User Story 2 (T024-T027) - Dependencies and working app
5. **STOP and VALIDATE**: Run `streamlit run app.py` and verify placeholder page loads
6. **MVP COMPLETE** - Basic scaffolding with working app

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T005)
2. Add User Story 1 → Directory structure with placeholder modules (T006-T023)
3. Add User Story 2 → Working app with dependencies (T024-T027) → **MVP Demo Point**
4. Add User Story 3 → Code quality tools configured (T028-T035)
5. Add User Story 4 → Proper imports and config module (T036-T042)
6. Add Polish → Final validation and documentation (T043-T047)

Each increment adds value without breaking previous work.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T005)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T006-T023) - 23 tasks, many parallelizable
   - **Developer B**: Wait for US1, then User Story 2 (T024-T027) - 4 tasks
   - **Developer C**: User Story 3 (T028-T035) in parallel with US2 - 8 tasks
3. After US1 complete:
   - **Developer A or D**: User Story 4 (T036-T042) - 7 tasks
4. **All together**: Polish phase (T043-T047)

**Optimal**: 2-3 developers can complete in ~2-4 hours with parallelization.

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] ✅ All 47 tasks completed
- [ ] ✅ Directory structure matches plan.md (capassigner/core/, capassigner/ui/, tests/ with subdirectories)
- [ ] ✅ `conda create --prefix ./.conda python=3.9 && conda activate ./.conda && pip install -r requirements.txt` succeeds
- [ ] ✅ `streamlit run app.py` launches and displays "Welcome to CapAssigner" page
- [ ] ✅ `ruff check capassigner/` passes with zero errors
- [ ] ✅ `black --check capassigner/` passes
- [ ] ✅ `isort --check capassigner/` passes
- [ ] ✅ `mypy capassigner/` passes with zero errors
- [ ] ✅ `pytest` discovers test structure and reports "0 tests collected" (no errors)
- [ ] ✅ `python -c "import capassigner.core; import capassigner.ui; from capassigner.config import DEFAULT_N_MAX_SP"` succeeds
- [ ] ✅ Constitutional compliance: `grep -r "import streamlit" capassigner/core/` returns empty
- [ ] ✅ All __init__.py files present in packages and test directories
- [ ] ✅ All placeholder modules have module docstrings and type hints
- [ ] ✅ .gitignore excludes .conda/, __pycache__/, .pytest_cache/, .mypy_cache/
- [ ] ✅ README.md documents conda setup, installation, and running instructions

---

## Notes

- **[P]** tasks = different files, no dependencies - can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after logical groups (e.g., all core modules, all config files)
- Stop at checkpoints to validate story independently
- **No tests**: Feature specification did not request test-driven development
- **Conda environment**: User requirement for `.conda/` directory at project root is reflected in all documentation tasks
- **Constitutional compliance**: Task T042 explicitly verifies core/ has no streamlit imports

---

## Summary

**Total Tasks**: 47 tasks across 7 phases
**Task Count by User Story**:
- Setup: 2 tasks (T001-T002)
- Foundational: 3 tasks (T003-T005)
- User Story 1 (P1): 18 tasks (T006-T023) - **Most complex**, creates all directories and modules
- User Story 2 (P1): 4 tasks (T024-T027) - Dependencies and working app
- User Story 3 (P2): 8 tasks (T028-T035) - Code quality configurations
- User Story 4 (P2): 7 tasks (T036-T042) - Module initialization and imports
- Polish: 5 tasks (T043-T047) - Final validation and documentation

**Parallel Opportunities**: 28 tasks marked with [P] can run in parallel within their phase
**Independent Test Criteria**: Each user story includes specific checkpoint validation
**Suggested MVP Scope**: User Stories 1 + 2 (Setup → Foundational → US1 → US2 = working scaffolded app)
**Format Validation**: ✅ All tasks follow checklist format (checkbox, ID, [P]/[Story] labels, file paths)

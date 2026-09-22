99y670# Implementation Plan: PDF Exhaustive Regression Tests

**Branch**: `001-pdf-exhaustive-tests` | **Date**: 2025-12-12 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-pdf-exhaustive-tests/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add automated regression tests from two PDF example circuits to prevent regressions in the SP Tree exhaustive solver. Current "SP Tree Exhaustive" does not find the expected equivalent capacitance for these cases. The tests will validate both the equivalent capacitance calculation for explicit circuit topologies and the exhaustive search algorithm's ability to find matching solutions.

## Technical Context

**Language/Version**: Python 3.7.4+  
**Primary Dependencies**: pytest ≥5.0, numpy ≥1.24 (already in project dependencies per constitution)  
**Storage**: N/A (tests operate on in-memory data structures)  
**Testing**: pytest (existing test suite structure: tests/unit/, tests/integration/, tests/contract/)  
**Target Platform**: Local development environment (Windows/Linux/macOS)  
**Project Type**: Single project (test extension for existing codebase)  
**Performance Goals**: Test completion <10 seconds for both exercises (4 capacitors each, exhaustive search)  
**Constraints**: Tests must be deterministic, use SI units (Farads), provide clear failure messages  
**Scale/Scope**: 2 reference exercises, each with 4 capacitors, targeting µF-scale equivalent capacitances (5.96µF and 9.73µF)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Modular Architecture
✅ **PASS**: Tests extend the existing test suite without mixing concerns. Tests will be added to `tests/unit/` or `tests/contract/` following the existing pattern. No Streamlit dependencies involved.

### II. UX First
✅ **PASS**: This is a testing feature with no direct UI impact. Tests will provide clear, actionable error messages that help developers understand failures.

### III. Robust Input Parsing
✅ **PASS**: Tests explicitly use SI units (Farads) per FR-004 and validate correct handling of µF-scale values.

### IV. Algorithmic Correctness
✅ **PASS**: Tests validate both series/parallel formulas and Laplacian method equivalence calculations against known analytical results. This directly supports algorithmic correctness validation.

### V. Deterministic Reproducibility
✅ **PASS**: Tests are deterministic (FR-005) with no randomness involved, ensuring reproducible validation.

### Environment Setup
✅ **PASS**: Tests will be run within the existing conda environment (`.conda/`) using the standard `pytest tests/` workflow documented in the constitution.

**Result**: All gates PASS. No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
capassigner/
├── core/
│   ├── sp_enumeration.py      # Exhaustive search algorithm to be validated
│   ├── sp_structures.py       # Series/parallel tree structures for Ceq computation
│   └── metrics.py             # Error calculations for tolerance checking

tests/
├── unit/
│   ├── test_sp_enumeration.py       # Existing SP enumeration tests
│   ├── test_sp_structures.py        # Existing SP structures tests
│   └── test_pdf_exhaustive.py       # NEW: PDF reference exercise validation
└── contract/
    └── test_algorithm_contracts.py  # Potential location for explicit topology tests
```

**Structure Decision**: This is a testing feature that extends the existing single-project structure. New tests will be added to `tests/unit/test_pdf_exhaustive.py` to validate the exhaustive search algorithm against the two PDF reference exercises. The tests will leverage existing modules from `capassigner/core/` without modifying them, focusing purely on validation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. This section is not applicable.

## Post-Design Constitution Re-Evaluation

*Completed after Phase 1 design (research, data model, contracts, quickstart)*

### I. Modular Architecture
✅ **PASS (Re-confirmed)**: Design maintains strict separation. Test file `test_pdf_exhaustive.py` imports only from `capassigner/core/` modules (sp_enumeration, sp_structures) and test fixtures. No cross-contamination with UI layer.

### II. UX First
✅ **PASS (Re-confirmed)**: Test design includes detailed error messages with exercise ID, observed/expected values, and relative error. Developers will have clear diagnostics for failures.

### III. Robust Input Parsing
✅ **PASS (Re-confirmed)**: Data model explicitly uses SI units with scientific notation (e.g., `1.5e-05` for 15 µF). Includes validation rules to catch unit errors.

### IV. Algorithmic Correctness
✅ **PASS (Re-confirmed)**: Two-tier validation strategy separates concerns:
1. Explicit topology tests validate `calculate_sp_ceq()` correctness
2. Exhaustive search tests validate `find_best_sp_solutions()` algorithm
This design ensures any failure can be attributed to the correct component.

### V. Deterministic Reproducibility
✅ **PASS (Re-confirmed)**: Test data is hardcoded with no random generation. Uses `ToleranceLevel.EXACT` (1e-10) for consistent, deterministic validation.

### Environment Setup
✅ **PASS (Re-confirmed)**: Quickstart explicitly documents conda environment activation requirement. Tests run with standard `pytest` command.

**Final Result**: All constitutional principles maintained through design phase. No new violations introduced. Ready for implementation (Phase 2 - not part of this command).

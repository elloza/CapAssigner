# Implementation Plan: SP Graph Exhaustive

**Branch**: `005-sp-graph-exhaustive` | **Date**: December 12, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-sp-graph-exhaustive/spec.md`

## Summary

Implement a new "SP Graph Exhaustive" method that enumerates all connected multigraph topologies with $N$ edges (capacitors) and iteratively reduces them using Series-Parallel rules. This solves the "Classroom Problem" where valid SP circuits have internal nodes (bridge-like structures) that the current tree-based method misses.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: NetworkX (graph operations), Streamlit (UI)
**Storage**: N/A (In-memory computation)
**Testing**: pytest
**Target Platform**: Web (Streamlit)
**Project Type**: Web application
**Performance Goals**: N=6 enumeration in < 30 seconds
**Constraints**: Must handle internal nodes and iterative reduction
**Scale/Scope**: Core algorithm + UI integration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Modular Architecture**: Algorithm in `capassigner/core/sp_graph_exhaustive.py`, UI in `capassigner/ui/`. ✅
- **UX First**: New method added to selector with clear tooltip. Suggestions for high error. ✅
- **Robust Input Parsing**: Uses existing parsing. ✅
- **Algorithmic Correctness**: Iterative reduction must be mathematically exact. ✅
- **Deterministic Reproducibility**: Graph enumeration is deterministic. ✅

## Project Structure

### Documentation (this feature)

```text
specs/005-sp-graph-exhaustive/
├── plan.md              # This file
├── research.md          # Algorithm selection
├── data-model.md        # Entity definitions
├── quickstart.md        # Usage guide
├── contracts/           # API definitions
│   └── sp_graph_exhaustive.yaml
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
capassigner/
├── core/
│   ├── sp_graph_exhaustive.py  # NEW: Core algorithm
│   ├── graphs.py               # UPDATE: Support MultiGraph in GraphTopology
│   └── metrics.py              # Existing
├── ui/
│   ├── pages.py                # UPDATE: Add method to selector
│   ├── tooltips.py             # UPDATE: Add method tooltip
│   └── theory.py               # UPDATE: Add documentation
tests/
├── unit/
│   └── test_sp_graph_exhaustive.py # NEW: Unit tests
```

**Structure Decision**: Option 1 (Single project) - extending existing structure.

## Complexity Tracking

N/A - No constitution violations.

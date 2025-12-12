<!--
Sync Impact Report:
- Version change: 0.0.0 → 1.0.0
- Modified principles: N/A (initial constitution)
- Added sections: Core Principles (5), Environment Setup, Technology Stack, Development Workflow, Governance
- Removed sections: N/A
- Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ aligned with principles
  - .specify/templates/spec-template.md: ✅ aligned with user story structure
  - .specify/templates/tasks-template.md: ✅ aligned with phase structure
- Follow-up TODOs: None
-->

# CapAssigner Constitution

A web-based capacitor network synthesis tool for designing optimal component combinations.

## Core Principles

### I. Modular Architecture

The codebase MUST maintain strict separation between core algorithms and UI components:

- **Core modules** (`capassigner/core/`): Pure Python algorithms with no Streamlit dependencies
  - `sp_structures.py`: Series-parallel tree dataclasses and formulas
  - `sp_enumeration.py`: Exhaustive SP topology enumeration
  - `graphs.py`: Graph topology and Laplacian nodal analysis
  - `heuristics.py`: Random graph heuristic search
  - `metrics.py`: Error calculations and solution ranking
  - `parsing.py`: Capacitance value parsing and formatting
- **UI modules** (`capassigner/ui/`): Streamlit-specific components
  - `pages.py`: Main page layout and navigation
  - `plots.py`: Circuit diagrams (SchemDraw, NetworkX)
  - `theory.py`: Educational content
  - `tooltips.py`: Help text

**Rationale**: Enables independent testing of algorithms without UI dependencies and facilitates future CLI or API interfaces.

### II. UX First

User experience MUST be prioritized in all UI decisions:

- Clear, responsive interface with immediate feedback
- Progress bars for computations exceeding 1 second
- Actionable error messages with format examples
- Human-readable capacitance display (e.g., "5.2pF" not "5.2e-12F")
- Visual indicators for tolerance status (✓ green / ✗ red)
- Educational content accessible via expandable sections

**Rationale**: Engineers need confidence in results. Clear feedback builds trust and reduces errors.

### III. Robust Input Parsing

The system MUST accept all common capacitance notation formats:

- Unit suffixes: `pF`, `nF`, `µF`, `uF`, `mF`, `F` (capital F required)
- Scientific notation: `1e-12`, `1.2e-11`, `1*10^-12`
- Plain decimals: `0.0000000000052`
- Negative and zero values MUST be rejected with clear messages
- Invalid formats MUST show actionable error with examples

**Rationale**: Engineers use diverse notation across tools. Flexible parsing eliminates friction.

### IV. Algorithmic Correctness

All capacitance calculations MUST be mathematically correct:

- **Series formula**: $C_s = \frac{1}{\frac{1}{C_1} + \frac{1}{C_2} + \cdots + \frac{1}{C_n}}$
- **Parallel formula**: $C_p = C_1 + C_2 + \cdots + C_n$
- **Laplacian method**: Nodal admittance matrix with boundary conditions $V_A=1$, $V_B=0$
- Singular matrix handling with pseudo-inverse
- Disconnected network detection returning $C_{eq}=0$

**Rationale**: Circuit theory must be faithfully implemented. Incorrect results undermine engineering decisions.

### V. Deterministic Reproducibility

Heuristic searches MUST be reproducible:

- Same seed + same parameters → identical results
- Random seed exposed in UI for user control
- Results MUST be sorted by absolute error (ascending)

**Rationale**: Reproducibility enables verification and comparison of results.

## Environment Setup

**CRITICAL**: Before running ANY Python commands, tests, or the application, developers MUST ALWAYS activate the conda environment located in the repository root. Failure to activate the environment will cause import errors, version mismatches, and unpredictable behavior.

### Required Environment Activation

```bash
# Windows (cmd)
conda activate .\.conda

# Windows (PowerShell)
conda activate .\.conda

# Unix/macOS
conda activate ./.conda
```

**This applies to ALL operations**:
- Running the application (`streamlit run app.py`)
- Executing tests (`pytest tests/`)
- Installing packages (`pip install ...`)
- Running scripts or utilities
- Any Python command execution

The environment is located at the repository root in `.conda/` directory. The `environment.yml` file defines all dependencies.

**Quick Start**:
```bash
# Create environment (first time only)
conda env create -f environment.yml -p .conda

# Activate environment
conda activate .\.conda

# Run application
streamlit run app.py

# Run tests
pytest tests/ -v
```

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.7.4+ | Core implementation |
| UI Framework | Streamlit | ≥1.28 | Web interface |
| Numerical | NumPy | ≥1.24 | Matrix operations, Laplacian solving |
| Data | Pandas | ≥2.0 | Results tables |
| Plotting | Matplotlib | ≥3.7 | Graph visualization |
| Graphs | NetworkX | ≥3.1 | Graph topologies |
| Circuits | SchemDraw | ≥0.16 | SP circuit diagrams |
| Testing | pytest | ≥5.0 | Unit and integration tests |

## Development Workflow

### Project Structure

```
capassigner/
├── __init__.py
├── config.py              # Constants: MAX_SP_EXHAUSTIVE_N, E-series data
├── core/                  # Pure Python (no Streamlit)
│   ├── graphs.py
│   ├── heuristics.py
│   ├── metrics.py
│   ├── parsing.py
│   ├── sp_enumeration.py
│   └── sp_structures.py
└── ui/                    # Streamlit UI
    ├── pages.py
    ├── plots.py
    ├── theory.py
    └── tooltips.py

tests/
├── unit/                  # Algorithm tests
├── integration/           # Workflow tests
└── contract/              # API contract tests

specs/                     # Feature specifications
└── [###-feature]/
    ├── spec.md
    ├── plan.md
    ├── tasks.md
    └── ...
```

### Testing Requirements

- All core algorithms MUST have unit tests
- Integration tests MUST cover primary user workflows
- Tests MUST pass before merging (`pytest tests/ -v`)
- Target: 95%+ test pass rate

### Performance Targets

| Scenario | Target |
|----------|--------|
| SP Exhaustive (N=5) | < 3 seconds |
| SP Exhaustive (N=8) | < 30 seconds |
| Heuristic (2000 iterations) | < 10 seconds |
| Input parsing | < 10ms per value |

### Code Quality

- Type hints required for all public functions
- Docstrings required for modules and public functions
- No Streamlit imports in `capassigner/core/`
- Session state keys MUST be unique to prevent conflicts

## Governance

This constitution supersedes all other development practices for CapAssigner.

### Amendment Process

1. Propose change with rationale
2. Document impact on existing code
3. Update affected templates if principles change
4. Increment version according to semantic versioning:
   - **MAJOR**: Principle removal or backward-incompatible redefinition
   - **MINOR**: New principle or significant expansion
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements

### Compliance

- All code reviews MUST verify constitutional compliance
- Complexity violations MUST be justified in PR description
- Use `CLAUDE.md` for agent-specific runtime guidance

**Version**: 1.0.0 | **Ratified**: 2025-12-03 | **Last Amended**: 2025-12-03

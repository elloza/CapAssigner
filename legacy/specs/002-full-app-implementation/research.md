# Research: Complete CapAssigner Application

**Feature**: 002-full-app-implementation
**Date**: 2025-10-20
**Status**: Complete

## Overview

This document consolidates research findings for implementing the complete CapAssigner application. Since the Technical Context in plan.md was fully specified (no "NEEDS CLARIFICATION" items), this research focuses on best practices, algorithm implementation patterns, and integration strategies for the chosen technologies.

---

## Technology Best Practices

### Streamlit (UI Framework)

**Decision**: Use Streamlit for rapid web application development with minimal boilerplate

**Best Practices**:
1. **Session State Management**:
   - Use `st.session_state` for all stateful data (capacitor inventory, method selection, results)
   - Assign unique, stable keys to all widgets to prevent state loss on reruns
   - Initialize session state variables in a dedicated function called at app start

2. **Performance Optimization**:
   - Use `@st.cache_data` decorator for expensive pure functions (parsing, SP enumeration, graph C_eq)
   - Cache with stable parameters only; exclude callbacks and session-specific data
   - Clear cache selectively when user changes fundamental inputs (not on every interaction)

3. **Progress Feedback**:
   - Use `st.progress()` for visual progress bars
   - Use `st.empty()` containers for dynamic text updates during computation
   - Update progress in increments (e.g., every 50 iterations, not every iteration) to avoid excessive reruns

4. **Widget Organization**:
   - Group related widgets in `st.expander()` or `st.container()` for logical sections
   - Use columns (`st.columns()`) for compact parameter inputs
   - Place theory explanations in collapsible expanders to reduce visual clutter

**Rationale**: Streamlit's reactive model simplifies state management but requires careful caching and keying to avoid performance issues. The above patterns are proven in production Streamlit apps.

**Alternatives Considered**:
- Flask + React: Too much boilerplate for MVP
- Dash: Less intuitive API, smaller community
- Gradio: Limited customization for complex layouts

**References**:
- Streamlit docs: https://docs.streamlit.io/library/advanced-features/session-state
- Caching guide: https://docs.streamlit.io/library/advanced-features/caching

---

### NumPy (Numerical Operations)

**Decision**: Use NumPy for matrix operations in Laplacian-based nodal analysis

**Best Practices**:
1. **Matrix Solving**:
   - Use `np.linalg.solve()` for non-singular systems (Ax = b)
   - Catch `np.linalg.LinAlgError` for singular matrices and fall back to `np.linalg.pinv()` (pseudo-inverse)
   - Use `np.linalg.cond()` to check condition number before solving (detect near-singular matrices)

2. **Numerical Stability**:
   - Add small regularization term (e.g., 1e-12 * I) to Laplacian diagonal for ill-conditioned matrices
   - Use double precision (default `np.float64`) for all capacitance calculations
   - Check for `np.isnan()` and `np.isinf()` in results and handle gracefully

3. **Performance**:
   - Use vectorized operations instead of loops (e.g., `C_parallel = capacitors.sum()`)
   - Preallocate arrays for known sizes (e.g., Laplacian matrix for fixed number of nodes)
   - Use in-place operations where possible (e.g., `+=`, `*=`)

**Rationale**: NumPy's linear algebra routines are battle-tested and highly optimized. Proper error handling for singular matrices is critical for robustness (Constitutional Principle I: Scientific Accuracy).

**Edge Cases**:
- Disconnected networks: Laplacian is singular. Solution: Check connectivity first using NetworkX or detect singular matrix and return C_eq=0.
- Floating nodes: Lead to rank-deficient matrices. Solution: Detect via `np.linalg.matrix_rank()` and warn user.

---

### NetworkX (Graph Representation and Visualization)

**Decision**: Use NetworkX for general graph topology representation and visualization

**Best Practices**:
1. **Graph Construction**:
   - Use `nx.Graph()` for undirected capacitor networks (capacitors are bidirectional)
   - Store capacitance values as edge attributes: `G.add_edge(u, v, capacitance=5.2e-12)`
   - Designate terminals as special nodes with labels 'A' and 'B'

2. **Connectivity Checks**:
   - Use `nx.has_path(G, 'A', 'B')` to detect disconnected networks before Laplacian analysis
   - Use `nx.number_connected_components(G)` to count isolated subgraphs
   - Warn user if network has floating nodes (degree 0 or disconnected from A-B path)

3. **Visualization**:
   - Use `nx.spring_layout()` or `nx.kamada_kawai_layout()` for automatic node positioning
   - Use `nx.draw_networkx()` with custom node colors (terminals in one color, internal nodes in another)
   - Label edges with capacitance values formatted in human-readable units (pF, nF)

4. **Random Graph Generation** (for heuristic search):
   - Use `nx.gnm_random_graph(n, m, seed=seed)` for deterministic random graphs (fixed seed)
   - Generate graphs with `n = 2 + max_internal_nodes` (A, B plus internal nodes)
   - Ensure A and B are always present; add random internal nodes and edges with random capacitors

**Rationale**: NetworkX provides robust graph algorithms and integrates well with Matplotlib for visualization. Using edge attributes for capacitance keeps data and topology together.

**Alternatives Considered**:
- igraph: Faster but less Pythonic API
- graph-tool: C++ backend, harder to install
- Custom graph implementation: Reinventing the wheel, high bug risk

---

### SchemDraw (Circuit Diagram Rendering)

**Decision**: Use SchemDraw for series-parallel circuit diagram generation

**Best Practices**:
1. **Component Labeling**:
   - Use `elm.Capacitor().label(f'C1={value_str}')` to annotate each capacitor with name and value
   - Position labels above or beside components for clarity (avoid overlap)
   - Use consistent units in labels (e.g., always pF for small capacitances)

2. **Topology Rendering**:
   - Recursively traverse SP tree structure to build circuit
   - Series nodes: connect components sequentially (`.right()`, `.down()`)
   - Parallel nodes: use `.split()` and `.join()` or draw branches with `.down()` and `.up()`

3. **Terminal Marking**:
   - Label terminals as 'A' and 'B' using `elm.Dot().label('A')` at circuit endpoints
   - Use consistent orientation (e.g., A on left, B on right)

4. **Styling**:
   - Use default SchemDraw style for professional appearance
   - Optionally adjust `Drawing(unit=3)` for size scaling
   - Render to SVG or PNG for embedding in Streamlit (`st.pyplot()` or `st.image()`)

**Rationale**: SchemDraw generates publication-quality circuit diagrams with minimal code. Recursive traversal of SP trees maps naturally to circuit drawing.

**Edge Cases**:
- Single capacitor: Draw simple A--[C]--B diagram
- All parallel: Draw multiple branches between A and B
- All series: Draw linear chain from A to B

**References**:
- SchemDraw docs: https://schemdraw.readthedocs.io/

---

## Algorithm Implementation Patterns

### Series-Parallel Enumeration (Dynamic Programming)

**Algorithm**: Generate all SP topologies using recursive enumeration with memoization

**Implementation Strategy**:
1. **Representation**: Define `SPNode` as a dataclass with variants:
   - `Leaf(capacitor_index, value)`: Single capacitor
   - `Series(left: SPNode, right: SPNode)`: Series connection
   - `Parallel(left: SPNode, right: SPNode)`: Parallel connection

2. **Enumeration**:
   - Base case: For 1 capacitor, return `[Leaf(0, capacitors[0])]`
   - Recursive case: For N capacitors, partition into two non-empty subsets, enumerate SP topologies for each subset, then combine with Series and Parallel operators
   - Complexity: Catalan(N) topologies × N! permutations ≈ O(4^N / N^1.5) × N!

3. **Memoization**:
   - Key: Frozenset of capacitor indices (order-independent)
   - Value: List of SPNode topologies
   - Use `@functools.lru_cache` or manual dict caching

4. **Capacitance Calculation**:
   - Leaf: Return capacitor value
   - Series: `C_series = 1 / (1/C_left + 1/C_right)` (recursive)
   - Parallel: `C_parallel = C_left + C_right` (recursive)

5. **Topology Expression**: Generate string representation (e.g., "((C1||C2)+C3)") during traversal

**Rationale**: Recursive enumeration with memoization avoids redundant computation and naturally represents SP structure. Frozenset keys ensure order-independence.

**Performance**:
- N=5: ~100 topologies, <1s
- N=8: ~10,000 topologies, ~3s (limit enforced by config)
- N=10: ~1M topologies, >30s (prohibited by default)

**References**:
- Catalan numbers: https://en.wikipedia.org/wiki/Catalan_number
- SP enumeration algorithms: Research papers on network synthesis

---

### Laplacian-Based Nodal Analysis (Matrix Method)

**Algorithm**: Solve nodal equations using Laplacian matrix for general graph topologies

**Implementation Strategy**:
1. **Laplacian Construction**:
   - For graph G with nodes {A, B, n1, n2, ...} and edges with capacitances C_ij:
   - Laplacian L where L[i][i] = sum of capacitances at node i (diagonal)
   - L[i][j] = -C_ij if edge exists between i and j (off-diagonal)
   - In frequency domain: Y = s·C becomes Y = j·ω·C, but for DC/quasi-static analysis, use s=1

2. **Boundary Conditions**:
   - Set V_A = 1, V_B = 0 (apply test voltage)
   - Eliminate rows/columns for A and B from Laplacian
   - Solve for internal node voltages using reduced system

3. **Current Calculation**:
   - After solving for node voltages, calculate current I_A = sum of (C_ij * (V_i - V_j)) for all edges connected to A
   - Equivalent capacitance: C_eq = I_A / (V_A - V_B) = I_A / 1 = I_A (in Farads when s=1)

4. **Error Handling**:
   - Singular matrix (disconnected network): Return C_eq = 0 with explanation "No path between A and B"
   - Near-singular matrix (poor conditioning): Use pseudo-inverse `np.linalg.pinv()` and warn user
   - Floating nodes: Detect via rank deficiency and suggest removing or connecting them

**Rationale**: Laplacian method is general (works for any topology, not just SP) and mathematically rigorous. It's the standard approach in circuit simulation.

**Edge Cases**:
- Bridge network: Y-Δ transform not needed; Laplacian handles directly
- Disconnected A-B: Laplacian is singular; determinant = 0
- Single capacitor A--[C]--B: Laplacian reduces to C_eq = C (trivial but good sanity check)

**References**:
- Nodal analysis: Circuit theory textbooks (e.g., Nilsson & Riedel, "Electric Circuits")
- Laplacian matrices: https://en.wikipedia.org/wiki/Laplacian_matrix

---

### Heuristic Graph Search (Random Generation)

**Algorithm**: Generate random graph topologies and evaluate with Laplacian method

**Implementation Strategy**:
1. **Random Graph Generation**:
   - Use `nx.gnm_random_graph(n_nodes, n_edges, seed=seed)` with fixed seed for determinism
   - `n_nodes = 2 + max_internal_nodes` (A, B plus internal nodes)
   - `n_edges` sampled uniformly from available capacitor inventory (with replacement)
   - Ensure graph is connected (check with `nx.is_connected(G)`); regenerate if not

2. **Edge Assignment**:
   - Randomly sample capacitors from inventory for each edge
   - Allow duplicate capacitors (same value on multiple edges)
   - Optionally enforce no duplicate edges (use set of (u, v) pairs)

3. **Iteration and Ranking**:
   - Generate `iters` random graphs (e.g., 2000)
   - Evaluate C_eq for each using Laplacian method
   - Track best solutions (lowest error) during search
   - Return top-K solutions sorted by error

4. **Progress Reporting**:
   - Call `progress_cb(iteration=i, total=iters, best_error=min_error)` every N iterations
   - Display current iteration count and best error found so far

**Rationale**: Random search is simple and explores non-SP topologies that exhaustive SP misses. Determinism (via fixed seed) is critical for reproducibility.

**Performance**:
- 2000 iterations with 2 internal nodes: ~5-10s (dominated by Laplacian solves)
- Increasing `max_internal_nodes` increases graph size and solve time

**Improvements** (out of scope for MVP):
- Simulated annealing: Accept worse solutions with decreasing probability to escape local minima
- Genetic algorithms: Crossover and mutation of graph topologies
- Particle swarm optimization: Swarm of candidate graphs evolving toward target

---

## Integration Considerations

### Core ↔ UI Integration

**Pattern**: Use optional `progress_cb` parameter in all core functions for UI updates

**Example Signature**:
```python
from typing import Callable, Optional

ProgressCallback = Callable[[int, int, str], None]  # (current, total, message)

def enumerate_sp_topologies(
    capacitors: list[float],
    progress_cb: Optional[ProgressCallback] = None
) -> list[SPNode]:
    """Enumerate all SP topologies with optional progress reporting."""
    for i, topology in enumerate(topologies):
        if progress_cb and i % 50 == 0:
            progress_cb(i, total_topologies, f"Exploring topology {i}/{total_topologies}")
    return results
```

**UI Wiring** (in `capassigner/ui/pages.py`):
```python
import streamlit as st

def on_progress(current: int, total: int, message: str):
    st.session_state.progress_bar.progress(current / total)
    st.session_state.progress_text.text(message)

# Create placeholders before calling core function
progress_bar = st.progress(0)
progress_text = st.empty()
st.session_state.progress_bar = progress_bar
st.session_state.progress_text = progress_text

# Call core function with callback
results = enumerate_sp_topologies(capacitors, progress_cb=on_progress)
```

**Rationale**: This pattern maintains core/UI separation while enabling responsive progress updates. Core functions remain testable without Streamlit.

---

### Input Parsing Strategy

**Pattern**: Parse-validate-format pipeline

**Steps**:
1. **Parse**: Convert string input to float (Farads)
   - Regex match for unit suffixes, scientific notation, plain decimals
   - Return `Result[float, str]` (success value or error message)

2. **Validate**: Check parsed value is in acceptable range
   - Reject negative or zero values (for target capacitance)
   - Warn if outside typical range (1fF to 1F)
   - Return validation errors with actionable messages

3. **Format**: Convert float back to human-readable string
   - Choose appropriate unit (pF for <1nF, nF for <1µF, etc.)
   - Format with 2-4 significant figures
   - Example: `5.2e-12 → "5.2pF"`

**Error Message Examples**:
- Input: `"5pf"` → Error: `"Invalid format '5pf' — use '5pF' with capital F"`
- Input: `"-3pF"` → Error: `"Capacitance cannot be negative. Enter positive value (e.g., '3pF')"`
- Input: `"abc"` → Error: `"Cannot parse 'abc'. Expected formats: '5.2pF', '1e-11', '0.000000000052'"`

**Rationale**: Clear error messages reduce user frustration and align with Constitutional Principle III (Robust Input Handling).

---

### Testing Strategy

**Test Coverage by Module**:

1. **`test_parsing.py`**:
   - Unit suffixes: pF, nF, µF, uF, mF, F (6 tests)
   - Scientific notation: 1e-11, 1.2e-12, 1*10^-11, 1.2*10^-12 (4 tests)
   - Plain decimals: 0.0000000001, 5.2 (2 tests)
   - Edge cases: negative, zero, very large/small, invalid strings (5 tests)
   - **Total**: ~17 tests

2. **`test_sp_structures.py`**:
   - Series formula: 1/C_s = 1/C1 + 1/C2 (multiple value combinations)
   - Parallel formula: C_p = C1 + C2 (multiple value combinations)
   - Nested structures: ((C1||C2)+C3) (correctness check)
   - **Total**: ~10 tests

3. **`test_sp_enumeration.py`**:
   - Small N regression tests (N=2, 3, 4 with known results)
   - Memoization correctness (same input → same output)
   - Topology expression generation (verify string format)
   - **Total**: ~8 tests

4. **`test_graphs.py`**:
   - Simple series: A--[C1]--[C2]--B → C_eq = 1/(1/C1 + 1/C2)
   - Simple parallel: A--[C1]--B, A--[C2]--B → C_eq = C1 + C2
   - Bridge network: Known result for Wheatstone bridge topology
   - Disconnected network: A--[C1], B (no path) → C_eq = 0
   - Singular matrix handling: Verify graceful failure
   - **Total**: ~12 tests

5. **`test_heuristics.py`**:
   - Determinism: Same seed → same results (multiple runs)
   - Parameter variation: Different seeds → different results
   - Edge cases: max_internal_nodes=0 (only A and B)
   - **Total**: ~6 tests

6. **`test_metrics.py`**:
   - Absolute error calculation: |C_eq - C_target|
   - Relative error calculation: (|C_eq - C_target| / C_target) × 100%
   - Division by zero when C_target=0 (should return infinity or N/A)
   - Tolerance checking: ±5% threshold
   - **Total**: ~8 tests

7. **`test_workflows.py`** (integration):
   - End-to-end scenario from User Story 1 (target=3.1pF, capacitors=[1pF, 2pF, 5pF])
   - Verify top solution is within tolerance
   - Check diagram generation doesn't crash
   - **Total**: ~5 tests

**Minimum Coverage**: 60% of core/ modules (pytest-cov), 100% of critical paths (parsing, formula calculations)

**Rationale**: Comprehensive unit tests ensure correctness (Constitutional Principle I: Scientific Accuracy). Integration tests verify user scenarios work end-to-end.

---

## Key Decisions Summary

| Decision | Chosen Option | Rationale |
|----------|---------------|-----------|
| UI Framework | Streamlit | Rapid development, minimal boilerplate, reactive model |
| Matrix Solving | NumPy linalg | Battle-tested, handles singular matrices, performant |
| Graph Library | NetworkX | Robust algorithms, good visualization, Pythonic API |
| Circuit Diagrams | SchemDraw | Publication-quality, integrates with Matplotlib, simple API |
| SP Algorithm | Recursive enumeration with memoization | Natural representation, avoids redundant computation |
| Heuristic Search | Random graph generation | Simple, explores non-SP space, deterministic with seed |
| Input Parsing | Regex + validation pipeline | Handles all formats, clear error messages |
| Testing | pytest with unit/integration split | Standard Python testing, good coverage tools |

---

## Open Questions Resolved

1. **How to handle singular matrices in Laplacian method?**
   - **Resolution**: Catch `LinAlgError`, check connectivity with NetworkX, return C_eq=0 for disconnected networks. Use pseudo-inverse for near-singular matrices.

2. **How to ensure determinism in heuristic search?**
   - **Resolution**: Use fixed random seed parameter. Expose seed in UI for reproducibility.

3. **How to display progress for long computations?**
   - **Resolution**: Use `progress_cb` parameter in core functions. Update Streamlit progress bar every N iterations (e.g., every 50).

4. **How to format capacitance values for display?**
   - **Resolution**: Write `format_capacitance(value: float) -> str` function that chooses appropriate unit (pF, nF, µF) based on magnitude and formats with 2-4 significant figures.

5. **How to test circuit diagram rendering?**
   - **Resolution**: Manual visual testing for MVP. Automated visual regression testing (e.g., with pytest-mpl) is future enhancement.

---

## Next Steps (Phase 1)

1. **Generate data-model.md**: Extract entities (Capacitor, Topology, Solution, etc.) from requirements and define schemas
2. **Generate contracts/**: Define function signatures for core modules (inputs, outputs, error cases)
3. **Generate quickstart.md**: Write user guide for running application and interpreting results
4. **Update agent context**: Run `update-agent-context.ps1` to add new technologies to agent-specific files

---

**Research Complete**: 2025-10-20

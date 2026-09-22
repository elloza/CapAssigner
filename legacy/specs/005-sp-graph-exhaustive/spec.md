# Feature Specification: SP Graph Exhaustive Method with UI/Documentation Updates

**Feature Branch**: `005-sp-graph-exhaustive`  
**Created**: December 12, 2025  
**Status**: Draft  
**Input**: User description: "Implementar nuevo método SP Graph Exhaustive que enumera grafos con nodos internos y aplica reducción serie-paralelo iterativa. Actualizar UI para diferenciar métodos y documentar sus fundamentos."

---

## Problem Statement

The current **SP Exhaustive** method generates only **binary tree topologies** where each capacitor appears exactly once. This fails to find solutions for circuits that are still **series-parallel reducible** but require:

1. **Internal nodes** (more than just terminals A and B)
2. **Capacitors placed between arbitrary node pairs**

**Example (Classroom Problem)**:
- Capacitors: 3pF, 2pF, 3pF, 1pF
- Target: 1.0pF
- SP Tree Best: 0.923pF (7.69% error) ❌
- SP Graph (correct): 1.0pF (0% error) ✅

The correct topology is:
```
A ---3pF--- C ---2pF--- D ---3pF--- B
                 ||
               1pF
```

This IS series-parallel reducible (2pF || 1pF = 3pF, then 3pF + 3pF + 3pF in series = 1pF), but cannot be represented as a binary tree.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - SP Graph Exhaustive Method (Priority: P1)

A professor wants to find the optimal capacitor network for a classroom problem. They have 4 capacitors [3pF, 2pF, 3pF, 1pF] and need exactly 1.0pF. The current SP Exhaustive gives 7.69% error. They need a method that can find topologies with internal nodes while still being deterministic and complete within the SP-reducible space.

**Why this priority**: This is the core algorithm that solves the original bug report. Without this, the classroom example cannot be solved exactly.

**Independent Test**: Run algorithm with [3, 2, 3, 1] pF targeting 1.0pF. Verify it returns exactly 1.0pF with 0% error.

**Acceptance Scenarios**:

1. **Given** capacitors [3pF, 2pF, 3pF, 1pF] and target 1.0pF, **When** user runs SP Graph Exhaustive, **Then** system finds solution with C_eq = 1.0pF (error < 0.001%)

2. **Given** capacitors that have an exact SP-tree solution, **When** user runs SP Graph Exhaustive, **Then** system finds the same solution as SP Tree Exhaustive

3. **Given** N ≤ 6 capacitors, **When** user runs SP Graph Exhaustive, **Then** computation completes in < 30 seconds

4. **Given** N > 6 capacitors, **When** user selects SP Graph Exhaustive, **Then** system shows warning about exponential complexity and suggests Heuristic Search

---

### User Story 2 - UI Method Selection Clarity (Priority: P2)

A student using the tool is confused about which method to use. They need clear explanations of when to use each method and what the trade-offs are.

**Why this priority**: Good UX is essential for educational tools. Users must understand what they're selecting.

**Independent Test**: Open method selector, verify each option has clear tooltip explaining when to use it.

**Acceptance Scenarios**:

1. **Given** user opens method selector dropdown, **When** they hover over each option, **Then** tooltip explains method in plain language with use-case examples

2. **Given** user selects a method, **When** computation starts, **Then** status text explains what the algorithm is doing

3. **Given** SP Tree method returns error > 5%, **When** results display, **Then** system suggests trying SP Graph or Heuristic method

---

### User Story 3 - Documentation of Methods (Priority: P3)

A user wants to understand the mathematical foundations of each method. They need comprehensive documentation explaining the theory, algorithms, and limitations.

**Why this priority**: Educational value - users should learn from the tool, not just use it.

**Independent Test**: Navigate to Theory section, verify all three methods are documented with formulas and examples.

**Acceptance Scenarios**:

1. **Given** user opens Theory section, **When** they view content, **Then** each method has its own subsection with mathematical foundations

2. **Given** user reads SP Graph documentation, **When** they see examples, **Then** the classroom 4-capacitor problem is shown step-by-step

3. **Given** user reads method comparison, **When** they view the table, **Then** complexity, completeness, and use-cases are clearly compared

---

### Edge Cases

- What happens when N > 6 capacitors with SP Graph Exhaustive? → Show warning, suggest Heuristic
- What happens when no SP-reducible solution exists? → Return best non-exact solution found
- What happens when graph is disconnected? → Skip invalid topologies
- How handle timeout for large N? → Progress bar with cancel option
- What if all capacitors have the same value? → May find duplicate solutions, deduplicate

---

## Requirements *(mandatory)*

### Functional Requirements

**Core Algorithm (SP Graph Exhaustive)**:

- **FR-001**: System MUST enumerate all possible placements of N capacitors on graphs with up to K internal nodes (K = N-1 max)
- **FR-002**: System MUST test each graph for SP-reducibility using iterative series/parallel detection
- **FR-003**: System MUST calculate exact C_eq for SP-reducible graphs
- **FR-004**: System MUST rank solutions by absolute error from target
- **FR-005**: System MUST support progress callback for UI updates every 50 graphs tested
- **FR-006**: System MUST complete in < 30 seconds for N ≤ 6 capacitors
- **FR-007**: System MUST warn user when N > 6 about exponential complexity

**SP-Reducibility Detection**:

- **FR-008**: System MUST detect parallel edges (same endpoints) and combine using C_parallel = C1 + C2
- **FR-009**: System MUST detect series nodes (degree-2 internal nodes) and combine using 1/C_series = 1/C1 + 1/C2
- **FR-010**: System MUST iterate reduction until graph is single edge A-B or no more reductions possible
- **FR-011**: System MUST mark graph as SP-reducible only if final result is single edge A-B

**UI Updates**:

- **FR-012**: Method selector MUST show three options: "SP Tree Exhaustive", "SP Graph Exhaustive", "Heuristic Graph Search"
- **FR-013**: Each method MUST have descriptive tooltip explaining use-case
- **FR-014**: Results MUST show suggestion to try other methods when error > 5%
- **FR-015**: Theory section MUST document all three methods with mathematical foundations

**Documentation**:

- **FR-016**: README MUST explain the difference between SP Tree and SP Graph methods
- **FR-017**: Theory section MUST include step-by-step example of classroom 4-cap problem
- **FR-018**: Theory section MUST include complexity comparison table

### Key Entities

- **SPGraph**: Graph with nodes (terminals + internal) and edges (capacitors with values)
- **SPReduction**: Record of a series or parallel reduction step
- **SPReductionResult**: Final C_eq or "not SP-reducible" with reduction history

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Classroom problem [3, 2, 3, 1] pF → 1.0pF returns exact solution with error < 0.001%
- **SC-002**: All existing SP Tree test cases also pass with SP Graph (superset)
- **SC-003**: N=4 capacitors enumerate in < 5 seconds
- **SC-004**: N=6 capacitors enumerate in < 30 seconds
- **SC-005**: Method tooltips rated "clear" by 3 test users (or self-review)
- **SC-006**: Theory section includes mathematical formulas for all reduction rules
- **SC-007**: 0 regressions in existing test suite (308 tests pass)

---

## Scope

### In Scope

- New `sp_graph_exhaustive.py` module with graph enumeration and SP-reduction
- UI updates to method selector with new option
- Tooltips for all methods
- Suggestion system when SP Tree gives high error
- Theory documentation for SP Graph method
- Updated README with method comparison

### Out of Scope

- Non-SP graph analysis (that's what Heuristic Search is for)
- Delta-Y transformations
- Graph visualization for SP Graph solutions (use existing network viz)
- Optimization of SP Tree Exhaustive (already fast enough)

---

## Dependencies & Assumptions

### Dependencies

- Existing `graphs.py` module for NetworkX graph utilities
- Existing `metrics.py` for Solution dataclass and error calculations
- Existing UI framework in `pages.py`
- Existing Theory section in `theory.py`

### Assumptions

- Users understand basic circuit theory (series/parallel)
- N ≤ 6 is practical limit for exhaustive graph enumeration
- SP-reducible graphs cover most educational use-cases

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Exponential complexity for large N | Poor UX, timeouts | Limit to N ≤ 6 with warning, suggest Heuristic for larger |
| Algorithm correctness | Wrong answers | Comprehensive test suite with hand-calculated examples |
| Confusion between methods | User frustration | Clear tooltips and Theory documentation |
| Performance regression | Slow UI | Progress callbacks, async computation |

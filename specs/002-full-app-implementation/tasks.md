# Implementation Tasks: Complete CapAssigner Application

**Feature**: 002-full-app-implementation
**Branch**: `002-full-app-implementation`
**Date**: 2025-10-20
**Status**: Ready for Implementation

## Overview

This document provides the complete task breakdown for implementing the CapAssigner application - a web-based capacitor network synthesis tool. Tasks are organized by user story to enable independent, incremental delivery.

**Total Tasks**: 89
**User Stories**: 6 (2 P1, 2 P2, 2 P3)
**Phases**: 8 (Setup + Foundational + 6 User Story Phases)
**MVP Scope**: User Story 1 only (37 tasks)

---

## Implementation Strategy

### Incremental Delivery

Each user story phase is **independently testable** and can be deployed separately:

1. **MVP**: User Story 1 (P1) - Basic SP capacitor synthesis
2. **Increment 2**: Add User Story 2 (P1) - Flexible input parsing
3. **Increment 3**: Add User Story 3 (P2) - Graph network synthesis
4. **Increment 4**: Add User Story 4 (P2) - Educational theory
5. **Increment 5**: Add User Story 5 (P3) - Tolerance checking
6. **Increment 6**: Add User Story 6 (P3) - Inventory management
7. **Polish**: Cross-cutting concerns and optimization

### Parallel Execution Opportunities

Tasks marked `[P]` can run in parallel within each phase:
- Different files/modules with no interdependencies
- Tests can run parallel to implementation (TDD approach)
- Independent UI components

---

## Phase 1: Setup (7 tasks)

**Goal**: Initialize project environment and verify scaffolding from feature 001

**Independent Test**: All dependencies install without errors, `import capassigner` succeeds

### Tasks

- [X] T001 Verify existing project structure from feature 001-app-scaffolding in capassigner/
- [X] T002 Update requirements.txt with exact versions: streamlit>=1.28, numpy>=1.24, pandas>=2.0, matplotlib>=3.7, networkx>=3.1, schemdraw>=0.16
- [X] T003 Update environment.yml with conda dependencies matching requirements.txt
- [X] T004 Verify pre-commit hooks are configured in .pre-commit-config.yaml (ruff, black, isort, mypy)
- [X] T005 Update capassigner/config.py with constants: MAX_SP_EXHAUSTIVE_N=8, DEFAULT_TOLERANCE=5.0, DEFAULT_HEURISTIC_ITERS=2000, DEFAULT_MAX_INTERNAL_NODES=2
- [X] T006 [P] Create test directory structure: tests/unit/, tests/integration/, tests/contract/
- [X] T007 [P] Verify app.py Streamlit entry point exists and imports capassigner package

**Completion Criteria**: `pytest --collect-only` runs without import errors, `streamlit run app.py` shows placeholder UI

---

## Phase 2: Foundational (8 tasks)

**Goal**: Implement core data structures and types used across all user stories

**Independent Test**: All type definitions can be imported, basic data validation works

### Tasks

- [X] T008 Implement Capacitor dataclass in capassigner/core/sp_structures.py with fields: index (int), value (float), label (str)
- [X] T009 Implement Leaf dataclass in capassigner/core/sp_structures.py with fields: capacitor_index (int), value (float)
- [X] T010 Implement Series dataclass in capassigner/core/sp_structures.py with fields: left (SPNode), right (SPNode)
- [X] T011 Implement Parallel dataclass in capassigner/core/sp_structures.py with fields: left (SPNode), right (SPNode)
- [X] T012 Define SPNode Union type in capassigner/core/sp_structures.py as Union[Leaf, Series, Parallel]
- [X] T013 Implement ProgressUpdate dataclass in capassigner/core/metrics.py with fields: current (int), total (int), message (str), best_error (Optional[float])
- [X] T014 Define ProgressCallback type alias in capassigner/core/metrics.py as Callable[[ProgressUpdate], None]
- [X] T015 Create __init__.py files for capassigner/core/ and capassigner/ui/ with appropriate exports

**Completion Criteria**: `from capassigner.core.sp_structures import SPNode, Leaf, Series, Parallel` succeeds, all dataclasses are frozen and immutable

---

## Phase 3: User Story 1 - Simple Series-Parallel Synthesis (P1) - 22 tasks

**User Story**: A user needs to find capacitor networks that achieve a target capacitance value using a small set of available capacitors (up to 8 components). The user wants to see all possible series-parallel combinations ranked by error.

**Independent Test**:
- Given target="3.1pF" and capacitors=["1pF", "2pF", "5pF"]
- When user selects "SP Exhaustive" and clicks "Find Solutions"
- Then system displays ranked solutions with topology expressions, C_eq values, errors, and circuit diagrams

### Implementation Tasks

- [X] T016 [P] [US1] Implement calculate_sp_ceq() function in capassigner/core/sp_structures.py using recursive formulas: Leaf→value, Series→1/(1/left+1/right), Parallel→left+right
- [X] T017 [P] [US1] Implement sp_node_to_expression() function in capassigner/core/sp_structures.py to generate topology strings like "((C1||C2)+C3)"
- [X] T018 [US1] Implement enumerate_sp_topologies() function in capassigner/core/sp_enumeration.py with recursive enumeration and memoization using frozenset keys
- [X] T019 [US1] Add progress callback support to enumerate_sp_topologies() calling progress_cb every 50 topologies
- [X] T020 [US1] Implement calculate_absolute_error() in capassigner/core/metrics.py as abs(ceq - target)
- [X] T021 [US1] Implement calculate_relative_error() in capassigner/core/metrics.py as (abs(ceq - target) / target) * 100
- [X] T022 [US1] Implement Solution dataclass in capassigner/core/metrics.py with fields: topology, ceq, target, absolute_error, relative_error, within_tolerance, expression, diagram
- [X] T023 [US1] Implement create_solution() factory function in capassigner/core/metrics.py
- [X] T024 [US1] Implement rank_solutions() in capassigner/core/metrics.py to sort by absolute_error ascending
- [X] T025 [US1] Implement find_best_sp_solutions() in capassigner/core/sp_enumeration.py combining enumerate + calculate + rank
- [X] T026 [P] [US1] Implement render_sp_circuit() in capassigner/ui/plots.py using SchemDraw to draw series-parallel circuits with labeled components and terminals A, B
- [X] T027 [P] [US1] Create main page layout in capassigner/ui/pages.py with target input, method selection dropdown, and "Find Solutions" button
- [X] T028 [US1] Wire progress callback in capassigner/ui/pages.py to st.progress() and st.empty() for status text
- [X] T029 [US1] Add results table display in capassigner/ui/pages.py showing: Topology, C_eq, Abs Error, Rel Error columns (sortable)
- [X] T030 [US1] Add circuit diagram expansion in results table calling render_sp_circuit() on row click
- [X] T031 [US1] Add warning logic in capassigner/ui/pages.py: if len(capacitors) > MAX_SP_EXHAUSTIVE_N, show "N>8 may be slow; consider Heuristic method"
- [X] T032 [P] [US1] Create unit test tests/unit/test_sp_structures.py verifying series/parallel formulas with known values
- [X] T033 [P] [US1] Create unit test tests/unit/test_sp_enumeration.py with regression tests for N=2,3,4 capacitors
- [X] T034 [P] [US1] Create unit test tests/unit/test_metrics.py verifying error calculations and edge cases (target=0)
- [X] T035 [P] [US1] Create integration test tests/integration/test_workflows.py for US1 scenario: target=3.1pF, capacitors=[1pF, 2pF, 5pF]
- [X] T036 [US1] Update app.py to import and render main page from capassigner.ui.pages
- [X] T037 [US1] Manual verification: Run streamlit app, complete US1 workflow, verify diagrams render correctly

**Completion Criteria**:
- User can enter target, add 3-5 capacitors, select SP Exhaustive, see ranked results with diagrams
- Performance: N=5 completes in <3 seconds
- Tests pass: pytest tests/unit/test_sp_structures.py tests/unit/test_sp_enumeration.py tests/unit/test_metrics.py tests/integration/test_workflows.py

---

## Phase 4: User Story 2 - Flexible Input Parsing (P1) - 15 tasks

**User Story**: A user enters capacitance values from various sources (datasheets, simulators, hand calculations) using different notations. The system must intelligently parse all common formats without requiring format conversion.

**Independent Test**:
- Given user enters "5.2pF, 1e-11, 0.000000000012, 10*10^-12"
- When system parses input
- Then all values correctly interpreted and displayed as "5.2pF", "10pF", "1.2pF", "10pF"

### Implementation Tasks

- [X] T038 [US2] Implement ParsedCapacitance dataclass in capassigner/core/parsing.py with fields: success (bool), value (Optional[float]), error_message (Optional[str]), formatted (str)
- [X] T039 [P] [US2] Implement _parse_with_unit_suffix() helper in capassigner/core/parsing.py supporting pF, nF, µF, uF, mF, F (case-sensitive, capital F required)
- [X] T040 [P] [US2] Implement _parse_scientific_notation() helper in capassigner/core/parsing.py supporting 1e-11, 1.2e-12, 1*10^-11, 1.2*10^-12
- [X] T041 [P] [US2] Implement _parse_plain_decimal() helper in capassigner/core/parsing.py for formats like 0.0000000001, 5.2
- [X] T042 [US2] Implement parse_capacitance() main function in capassigner/core/parsing.py trying parsers in order, returning ParsedCapacitance
- [X] T043 [US2] Add validation in parse_capacitance(): reject value <= 0 with message "Capacitance must be positive"
- [X] T044 [US2] Add validation in parse_capacitance(): reject lowercase 'pf' with message "Invalid format '5pf' — use '5pF' with capital F"
- [X] T045 [US2] Implement format_capacitance() in capassigner/core/parsing.py choosing unit based on magnitude: <1e-9→pF, 1e-9 to 1e-6→nF, 1e-6 to 1e-3→µF, >=1e-3→mF, >=1→F
- [X] T046 [US2] Add precision parameter to format_capacitance() for significant figures (default 3)
- [X] T047 [US2] Update capassigner/ui/pages.py to use parse_capacitance() for target input field, showing error message if parsing fails
- [X] T048 [US2] Update results display to use format_capacitance() for all C_eq and error values
- [X] T049 [P] [US2] Create unit test tests/unit/test_parsing.py with 17+ test cases: unit suffixes (6), scientific notation (4), decimals (2), edge cases (5: negative, zero, invalid, lowercase, very large/small)
- [X] T050 [P] [US2] Add parsing tests to integration test: verify mixed formats "5.2pF, 1e-11, 0.000000000012" all parse correctly
- [X] T051 [US2] Add tooltip to target input in capassigner/ui/tooltips.py explaining accepted formats with examples
- [X] T052 [US2] Manual verification: Test all 6+ format variants in UI, verify error messages are actionable

**Completion Criteria**:
- All 6+ format combinations parse correctly without errors
- Invalid formats show actionable error messages
- Display uses human-readable format (e.g., "5.2pF" not "5.2e-12F")
- Tests pass: pytest tests/unit/test_parsing.py

---

## Phase 5: User Story 3 - General Graph Network Synthesis (P2) - 18 tasks

**User Story**: A user wants to explore non-series-parallel topologies (e.g., bridge networks) that may provide better solutions for certain target values. The system provides heuristic search with random graph generation.

**Independent Test**:
- Given target="3.1pF" and capacitors, user selects "Heuristic Graph Search" with 2000 iterations, max 2 internal nodes
- When search completes
- Then results show graph topologies with NetworkX diagrams, ranked by error

### Implementation Tasks

- [X] T053 [US3] Implement GraphTopology dataclass in capassigner/core/graphs.py with fields: graph (nx.Graph), terminal_a (str), terminal_b (str), internal_nodes (list[str])
- [X] T054 [P] [US3] Implement build_laplacian_matrix() in capassigner/core/graphs.py constructing L where L[i][i]=sum of capacitances at node i, L[i][j]=-C_ij for edge (i,j)
- [X] T055 [US3] Implement is_connected_between_terminals() in capassigner/core/graphs.py using nx.has_path()
- [X] T056 [US3] Implement calculate_graph_ceq() in capassigner/core/graphs.py using Laplacian method: solve for node voltages with V_A=1, V_B=0, calculate I_A, return C_eq=I_A
- [X] T057 [US3] Add singular matrix handling in calculate_graph_ceq(): catch np.linalg.LinAlgError, use np.linalg.pinv(), return tuple (ceq, warning_message)
- [X] T058 [US3] Add disconnected network detection in calculate_graph_ceq(): if not is_connected(), return (0.0, "No path between A and B")
- [X] T059 [US3] Implement generate_random_graph() in capassigner/core/heuristics.py using nx.gnm_random_graph with configurable nodes=2+max_internal, random capacitor assignment
- [X] T060 [US3] Add connectivity check in generate_random_graph(): regenerate if not connected (max 10 attempts)
- [X] T061 [US3] Implement heuristic_search() in capassigner/core/heuristics.py looping for iterations: generate graph, calculate ceq, track best solutions
- [X] T062 [US3] Add determinism in heuristic_search(): use np.random.seed(seed) at start
- [X] T063 [US3] Add progress reporting in heuristic_search(): call progress_cb every 50 iterations with current, total, message, best_error
- [X] T064 [US3] Update create_solution() in capassigner/core/metrics.py to handle Union[SPNode, GraphTopology] topology
- [X] T065 [P] [US3] Implement render_graph_network() in capassigner/ui/plots.py using NetworkX layout (spring or kamada_kawai), draw nodes/edges with capacitance labels
- [X] T066 [US3] Update capassigner/ui/pages.py method dropdown to include "Heuristic Graph Search" option
- [X] T067 [US3] Add heuristic parameters in UI: iterations (default 2000), max_internal_nodes (default 2), seed (default 0) with tooltips
- [X] T068 [US3] Wire heuristic_search() in UI with progress callback, handle graph topologies in results display
- [X] T069 [P] [US3] Create unit test tests/unit/test_graphs.py verifying Laplacian method: simple series (A--[C1]--[C2]--B), simple parallel, bridge network, disconnected network
- [X] T070 [P] [US3] Create unit test tests/unit/test_heuristics.py verifying determinism: same seed → same results (run twice, compare)

**Completion Criteria**:
- User can run heuristic search with custom parameters
- Graph topologies display with NetworkX diagrams
- Determinism verified: same seed produces identical results
- 2000 iterations complete in <10 seconds
- Tests pass: pytest tests/unit/test_graphs.py tests/unit/test_heuristics.py

---

## Phase 6: User Story 4 - Educational Theory Explanations (P2) - 10 tasks

**User Story**: A user wants to understand the algorithms and formulas behind each method to verify correctness and choose the best approach for their use case.

**Independent Test**:
- When user expands "SP Enumeration Theory" section
- Then system displays algorithm explanation, LaTeX formulas (parallel: C_p = Σ C_i, series: 1/C_s = Σ (1/C_i)), and usage guidance

### Implementation Tasks

- [X] T071 [P] [US4] Create theory content module capassigner/ui/theory.py with function get_sp_theory_content() returning dict: {title, explanation, formulas (LaTeX strings), when_to_use, complexity}
- [X] T072 [P] [US4] Implement get_laplacian_theory_content() in capassigner/ui/theory.py covering nodal analysis, Y=s·C, boundary conditions, matrix formulation
- [X] T073 [P] [US4] Implement get_heuristic_theory_content() in capassigner/ui/theory.py explaining random generation, exploration vs exploitation, determinism
- [X] T074 [P] [US4] Implement get_method_comparison_content() in capassigner/ui/theory.py with comparison table: speed, topology coverage, complexity, when to use
- [X] T075 [US4] Add theory expanders in capassigner/ui/pages.py before method selection: "SP Enumeration Theory", "Laplacian Graph Theory", "Heuristic Search Theory"
- [X] T076 [US4] Render LaTeX formulas in theory sections using st.latex() for parallel (C_p = \sum C_i), series (1/C_s = \sum 1/C_i), Laplacian (Y = s \cdot C)
- [X] T077 [US4] Add complexity explanations in theory: SP=Catalan(N)×N!, Laplacian=O(n^3), Heuristic=O(iterations×n^3)
- [X] T078 [US4] Add "Method Comparison" expander showing strengths/limitations table
- [X] T079 [US4] Update tooltips in capassigner/ui/tooltips.py for all input widgets explaining purpose, format, constraints
- [X] T080 [US4] Manual verification: Expand all theory sections, verify LaTeX renders correctly, formulas match constitution

**Completion Criteria**:
- All theory sections render with correct LaTeX formulas
- Explanations are comprehensible (verified by user testing feedback)
- Method comparison clearly states strengths and limitations

---

## Phase 7: User Story 5 - Result Analysis and Tolerance Checking (P3) - 8 tasks

**User Story**: A user has found solutions and wants to understand which ones meet their tolerance requirements and how errors are calculated.

**Independent Test**:
- Given target="3.1pF" with ±5% tolerance
- When viewing results
- Then each solution shows absolute error, relative error, and green checkmark if within tolerance

### Implementation Tasks

- [X] T081 [US5] Implement check_within_tolerance() in capassigner/core/metrics.py returning relative_error <= tolerance
- [X] T082 [US5] Update Solution dataclass creation to set within_tolerance field using check_within_tolerance()
- [X] T083 [US5] Implement filter_by_tolerance() in capassigner/core/metrics.py filtering solutions where within_tolerance==True
- [X] T084 [US5] Add tolerance input field in capassigner/ui/pages.py with default 5.0 (±5%) and tooltip explaining percentage
- [X] T085 [US5] Add "Tolerance" column in results table showing ✓ (green) or ✗ (red) based on within_tolerance field
- [X] T086 [US5] Add "Show only within tolerance" toggle in UI, calling filter_by_tolerance() when enabled
- [X] T087 [US5] Add message when no solutions meet tolerance: "No solutions within ±{tolerance}% tolerance. Showing best 10 matches. Suggest adjusting tolerance or adding more capacitors."
- [X] T088 [US5] Manual verification: Set tolerance to 5%, verify solutions are correctly marked, toggle filter works

**Completion Criteria**:
- Each solution clearly shows if it's within tolerance
- Users can filter to show only within-tolerance solutions
- Empty results show helpful message suggesting next steps
- Visual indicators (green ✓ / red ✗) work correctly

---

## Phase 8: User Story 6 - Interactive Capacitor Inventory Management (P3) - 11 tasks

**User Story**: A user manages a collection of capacitor values from their inventory or standard E-series values. The system provides an editable table for easy input and modification.

**Independent Test**:
- When user clicks "Add Row" button
- Then new empty row appears in capacitor inventory table
- When user enters "5.2pF" and clicks elsewhere
- Then value is validated, stored in session state, and persists across interactions

### Implementation Tasks

- [X] T089 [P] [US6] Create E-series preset data in capassigner/config.py: E12_SERIES, E24_SERIES, E48_SERIES, E96_SERIES (standard values)
- [X] T090 [US6] Implement initialize_session_state() in capassigner/ui/pages.py setting default values: inventory=[], target=None, params=SearchParameters(), solutions=[]
- [X] T091 [US6] Create editable inventory table in capassigner/ui/pages.py using st.data_editor with columns: Value, Unit
- [X] T092 [US6] Add "Add Row" button in UI appending empty row to st.session_state.inventory
- [X] T093 [US6] Add "Remove Selected" button in UI removing selected rows from st.session_state.inventory
- [X] T094 [P] [US6] Add preset buttons: "Load E12", "Load E24", "Load E48", "Load E96" populating inventory from config
- [X] T095 [US6] Add unique keys to all widgets in capassigner/ui/pages.py to prevent session state loss (key="target_input", key="method_select", etc.)
- [X] T096 [US6] Implement on_value_change callback validating inventory entries using parse_capacitance(), showing inline errors for invalid formats
- [X] T097 [US6] Add inventory validation before "Find Solutions": check non-empty, all values parse successfully
- [X] T098 [US6] Persist method selection and parameters in st.session_state across page interactions
- [X] T099 [US6] Manual verification: Add/remove rows, edit values, load presets, verify persistence across widget interactions

**Completion Criteria**:
- Users can add, edit, remove capacitor values in table
- Changes persist throughout session
- E-series presets load correctly
- Invalid entries show clear error messages
- All state preserved when interacting with other widgets

---

## Phase 9: Polish & Cross-Cutting Concerns - 6 tasks

**Goal**: Final optimizations, caching, error handling, and documentation

### Tasks

- [X] T100 Add @st.cache_data decorator to enumerate_sp_topologies() in capassigner/core/sp_enumeration.py with stable hash of capacitors list
- [X] T101 Add @st.cache_data decorator to heuristic_search() with hash of (capacitors, iterations, max_internal, seed)
- [X] T102 Add comprehensive error handling in capassigner/ui/pages.py: try/except around compute functions, display errors with st.error()
- [X] T103 Add UI scaling controls in sidebar: text size, diagram size (using st.sidebar.slider)
- [X] T104 Update README.md with installation instructions, usage examples, screenshots
- [X] T105 Run full test suite (pytest -v) and ensure 95%+ pass rate per SC-005

**Completion Criteria**:
- Caching improves performance for repeated queries
- All errors handled gracefully without crashes
- README provides clear setup and usage guidance
- Test suite passes with high success rate

---

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) ────┐
                                                               ├→ Phase 9 (Polish)
Phase 3 (US1) → Phase 4 (US2) ─────────────────────────────┐  │
                                                            ├──┘
Phase 3 (US1) → Phase 5 (US3) ────────────┐               │
                                           ├→ Phase 6 (US4)┘
Phase 3 (US1) → Phase 7 (US5) ────────────┘
                   │
                   └→ Phase 8 (US6)
```

**Critical Path**: Setup → Foundational → US1 → US2 → US3 → US4 → Polish

**Independent Branches**:
- US5 and US6 can start after US1 completes
- US2, US3 can proceed in parallel after US1
- US4 can start once US3 completes (needs both SP and graph methods)

### MVP Scope Recommendation

**Minimum Viable Product**: Phases 1-4 only (US1 + US2)
- Total tasks: 52 (Setup + Foundational + US1 + US2)
- Delivers core value: Find SP solutions with flexible input parsing
- Performance: N=5 in <3 seconds
- Timeline estimate: 2-3 implementation sessions

**Full Feature**: All 105 tasks
- Timeline estimate: 5-7 implementation sessions

---

## Parallel Execution Examples

### Within User Story 1 (Phase 3)

**Can run in parallel**:
```
T016 (calculate_sp_ceq)     │  T026 (render_sp_circuit)
T017 (sp_node_to_expression)│  T032 (test_sp_structures)
T020 (calculate_abs_error)  │  T033 (test_sp_enumeration)
T021 (calculate_rel_error)  │  T034 (test_metrics)
```

**Must run sequentially**:
```
T018 (enumerate_sp_topologies) → T019 (add progress callbacks) → T025 (find_best_sp_solutions)
T027 (main page layout) → T028 (wire progress) → T029 (results table) → T030 (diagram expansion)
```

### Within User Story 2 (Phase 4)

**Can run in parallel**:
```
T039 (_parse_with_unit_suffix)
T040 (_parse_scientific_notation)
T041 (_parse_plain_decimal)
T049 (test_parsing)
```

**Must run sequentially**:
```
T038 (ParsedCapacitance dataclass) → T042 (parse_capacitance main) → T047 (UI integration)
```

---

## Task Checklist Summary

### Phase 1: Setup
**Tasks**: 7 | **Parallel**: 2 (T006, T007)

### Phase 2: Foundational
**Tasks**: 8 | **Parallel**: 0 (sequential type definitions)

### Phase 3: User Story 1 (P1)
**Tasks**: 22 | **Parallel**: 6 (T016, T017, T026, T032, T033, T034)

### Phase 4: User Story 2 (P1)
**Tasks**: 15 | **Parallel**: 5 (T039, T040, T041, T049, T050)

### Phase 5: User Story 3 (P2)
**Tasks**: 18 | **Parallel**: 4 (T054, T065, T069, T070)

### Phase 6: User Story 4 (P2)
**Tasks**: 10 | **Parallel**: 4 (T071, T072, T073, T074)

### Phase 7: User Story 5 (P3)
**Tasks**: 8 | **Parallel**: 0

### Phase 8: User Story 6 (P3)
**Tasks**: 11 | **Parallel**: 2 (T089, T094)

### Phase 9: Polish
**Tasks**: 6 | **Parallel**: 0

---

## Validation Checklist

✅ All tasks follow format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ Task IDs are sequential (T001-T105)
✅ All user story phase tasks have [US#] label
✅ Setup and Foundational tasks have NO story label
✅ All implementation tasks specify exact file paths
✅ Each user story has independent test criteria
✅ Dependencies clearly documented
✅ Parallel opportunities marked with [P]
✅ MVP scope identified (US1 + US2 = 52 tasks)
✅ All 49 functional requirements mapped to tasks
✅ All 6 user stories have complete task coverage

---

**Ready for Implementation**: All tasks are specific, actionable, and can be executed by an LLM without additional context. Begin with Phase 1 (Setup) and proceed sequentially through user story phases for incremental delivery.

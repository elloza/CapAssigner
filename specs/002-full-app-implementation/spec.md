# Feature Specification: Complete CapAssigner Application

**Feature Branch**: `002-full-app-implementation`
**Created**: 2025-10-20
**Status**: Draft
**Input**: User description: "Quiero que implementes una primera versión de la aplicación con toda la funcionalidad."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simple Series-Parallel Capacitor Synthesis (Priority: P1)

A user needs to find capacitor networks that achieve a target capacitance value using a small set of available capacitors (up to 8 components). The user wants to see all possible series-parallel combinations ranked by error.

**Why this priority**: This is the core value proposition of CapAssigner - helping users design capacitor networks. Series-parallel topologies are the most common and practical configurations in real circuits.

**Independent Test**: Can be fully tested by entering a target capacitance (e.g., "3.1pF"), a list of available capacitors (e.g., "1pF, 2pF, 5pF"), selecting "SP Exhaustive" method, and verifying that results show all valid combinations ranked by error with circuit diagrams.

**Acceptance Scenarios**:

1. **Given** a target capacitance of "3.1pF" and available capacitors ["1pF", "2pF", "5pF"], **When** user selects "SP Exhaustive" method and clicks "Find Solutions", **Then** system displays ranked solutions showing topology expressions (e.g., "((C1||C2)+C3)"), equivalent capacitance values, absolute errors, relative errors, and visual circuit diagrams
2. **Given** user has found solutions, **When** user views a solution row, **Then** system shows a SchemDraw circuit diagram with labeled components (C1, C2, etc. with values) and terminals (A, B)
3. **Given** a target capacitance and 9 capacitors selected, **When** user selects "SP Exhaustive", **Then** system displays warning "N>8 may be slow; consider Heuristic method" before computation starts
4. **Given** valid input, **When** computation takes longer than 1 second, **Then** system shows progress bar with descriptive text (e.g., "Exploring 234/1000 topologies...")

---

### User Story 2 - Flexible Input Parsing (Priority: P1)

A user enters capacitance values from various sources (datasheets, simulators, hand calculations) using different notations. The system must intelligently parse all common formats without requiring format conversion.

**Why this priority**: Engineers use diverse notation across tools. Requiring manual format conversion creates friction and errors, undermining the application's usability and trustworthiness.

**Independent Test**: Can be tested by entering capacitance values in different formats (scientific notation, unit suffixes, decimals) and verifying that all are correctly parsed and displayed in human-readable format in results.

**Acceptance Scenarios**:

1. **Given** user enters capacitor values as "5.2pF, 1e-11, 0.000000000012, 10*10^-12", **When** system parses input, **Then** all values are correctly interpreted as Farads and displayed back in human-readable format (e.g., "5.2pF", "10pF", "1.2pF", "10pF")
2. **Given** user enters "5pf" (lowercase), **When** system validates input, **Then** system shows error message "Invalid format '5pf' — use '5pF' with capital F"
3. **Given** user enters target capacitance "2.5nF" or "µ2.5nF" (using µ symbol for micro), **When** system parses it, **Then** system correctly interprets it as 2.5e-9 Farads
4. **Given** user enters invalid format "abc", **When** system parses it, **Then** system shows clear error message explaining expected formats with examples

---

### User Story 3 - General Graph Network Synthesis (Priority: P2)

A user wants to explore non-series-parallel topologies (e.g., bridge networks) that may provide better solutions for certain target values. The system provides heuristic search with random graph generation.

**Why this priority**: While less common than SP networks, general graphs can achieve capacitance values impossible with pure SP topologies, expanding the solution space for challenging targets.

**Independent Test**: Can be tested by entering a target capacitance, selecting "Heuristic Graph Search" method, configuring parameters (iterations, max internal nodes, seed), and verifying that results show graph topologies with NetworkX visualizations.

**Acceptance Scenarios**:

1. **Given** target capacitance "3.1pF" and available capacitors, **When** user selects "Heuristic Graph Search" with 2000 iterations and max 2 internal nodes, **Then** system generates random graph topologies, evaluates them using Laplacian-based nodal analysis, and displays best solutions with NetworkX graph diagrams
2. **Given** user views a graph solution, **When** examining the diagram, **Then** system shows all nodes (terminals A, B plus internal nodes) and edges labeled with capacitor values
3. **Given** a long heuristic search, **When** computation is running, **Then** progress bar shows current iteration count and best error found so far (e.g., "Iteration 1234/2000, Best error: 0.03pF")
4. **Given** user sets same random seed twice, **When** running same search parameters, **Then** results are deterministic and identical

---

### User Story 4 - Educational Theory Explanations (Priority: P2)

A user wants to understand the algorithms and formulas behind each method to verify correctness and choose the best approach for their use case.

**Why this priority**: Transparency builds trust and enables informed decision-making. Engineers need to validate results against known circuit theory.

**Independent Test**: Can be tested by expanding theory sections for each method and verifying that formulas, explanations, and usage guidance are displayed clearly.

**Acceptance Scenarios**:

1. **Given** user is on the main page, **When** user expands "SP Enumeration Theory" section, **Then** system displays explanation of algorithm, key formulas (parallel: C_p = Σ C_i, series: 1/C_s = Σ (1/C_i)) rendered with LaTeX, and guidance on when to use this method
2. **Given** user is viewing "Laplacian Graph Method" theory, **When** reading content, **Then** system explains nodal analysis approach (Y = s·C, solving with V_a=1, V_b=0), shows matrix formulation, and describes handling of singular matrices and disconnected networks
3. **Given** user wants to compare methods, **When** viewing theory sections, **Then** each method clearly states strengths, limitations, and computational complexity
4. **Given** user sees result diagrams, **When** examining circuit drawings, **Then** all components are labeled with names and values (e.g., "C1=5.2pF") and terminals are clearly marked (A, B)

---

### User Story 5 - Result Analysis and Tolerance Checking (Priority: P3)

A user has found solutions and wants to understand which ones meet their tolerance requirements and how errors are calculated.

**Why this priority**: Engineers work with tolerances. Highlighting solutions that meet specifications saves manual filtering and reduces selection errors.

**Independent Test**: Can be tested by setting a tolerance threshold, running a search, and verifying that results show absolute error, relative error, and clear indication of which solutions are within tolerance.

**Acceptance Scenarios**:

1. **Given** user sets target "3.1pF" with ±5% tolerance, **When** viewing results, **Then** each solution shows: equivalent capacitance, absolute error (|C_eq - C_target|), relative error ((|C_eq - C_target| / C_target) × 100%), and visual indicator if within tolerance (green checkmark or similar)
2. **Given** multiple solutions exist, **When** results are displayed, **Then** solutions are ranked by absolute error (best match first)
3. **Given** user wants to filter results, **When** user toggles "Show only within tolerance", **Then** only solutions meeting tolerance criteria are displayed
4. **Given** no solutions meet tolerance, **When** viewing results, **Then** system displays message "No solutions within ±5% tolerance. Showing best 10 matches." and suggests adjusting tolerance or available capacitors

---

### User Story 6 - Interactive Capacitor Inventory Management (Priority: P3)

A user manages a collection of capacitor values from their inventory or standard E-series values. The system provides an editable table for easy input and modification.

**Why this priority**: Manual entry of many capacitor values is tedious. An editable table with add/remove functionality improves data entry efficiency.

**Independent Test**: Can be tested by adding, editing, and removing capacitor values from the inventory table and verifying that changes persist during the session and are used in calculations.

**Acceptance Scenarios**:

1. **Given** user opens the application, **When** user navigates to capacitor inventory section, **Then** system displays an editable table with columns for capacitor value and unit
2. **Given** user wants to add a capacitor, **When** user clicks "Add Row" button, **Then** a new empty row appears in the table
3. **Given** user has entered capacitor values, **When** user edits a value directly in the table, **Then** change is immediately reflected and persisted in session state
4. **Given** user wants to remove a capacitor, **When** user selects a row and clicks "Remove", **Then** row is deleted from the table
5. **Given** user wants to load standard values, **When** user selects "Load E12 series" preset, **Then** table is populated with E12 standard capacitor values

---

### Edge Cases

- What happens when user enters a target capacitance of zero or negative value?
- How does system handle when no capacitors are provided in inventory?
- What happens when all available capacitors are identical?
- How does system respond when Laplacian matrix is singular (disconnected network or floating nodes)?
- What happens when target capacitance is impossible to achieve with available components (e.g., target is larger than sum of all capacitors in parallel)?
- How does system handle extremely large capacitor sets (N > 20) in heuristic mode?
- What happens when user enters duplicate capacitor values in inventory?
- How does system behave when network has no path between terminals A and B?
- What happens when computation is interrupted or browser tab is closed during long search?

## Requirements *(mandatory)*

### Functional Requirements

#### Core Computation

- **FR-001**: System MUST correctly implement parallel capacitance formula: C_p = Σ C_i
- **FR-002**: System MUST correctly implement series capacitance formula: 1/C_s = Σ (1/C_i)
- **FR-003**: System MUST implement Laplacian-based nodal analysis for general graphs using Y = s·C matrix
- **FR-004**: System MUST solve nodal analysis with boundary conditions V_a=1, V_b=0
- **FR-005**: System MUST detect and handle singular matrices using regularization or pseudo-inverse
- **FR-006**: System MUST detect disconnected networks (no path between A and B) and return C_eq=0 with explanation
- **FR-007**: System MUST detect floating nodes and handle them gracefully without crashing

#### Input Parsing

- **FR-008**: System MUST parse capacitance values with unit suffixes: pF, nF, µF, uF (both µ and u), mF, F
- **FR-009**: System MUST parse scientific notation formats: 1e-11, 1.2e-12, 1*10^-11, 1.2*10^-12
- **FR-010**: System MUST parse plain decimal formats: 0.0000000001, 5.2, etc.
- **FR-011**: System MUST reject invalid or ambiguous input with actionable error messages showing expected format
- **FR-012**: System MUST display results in human-readable format (e.g., "5.2pF" not "5.2e-12F")

#### SP Enumeration

- **FR-013**: System MUST enumerate all series-parallel topologies for N ≤ 8 capacitors using dynamic programming
- **FR-014**: System MUST use memoization to avoid recomputing equivalent capacitances for identical subtrees
- **FR-015**: System MUST generate topology expressions showing structure (e.g., "((C1||C2)+C3)")
- **FR-016**: System MUST rank solutions by absolute error (smallest first)
- **FR-017**: System MUST limit SP exhaustive enumeration to N ≤ 8 by default (configurable in config.py)

#### Graph Heuristic Search

- **FR-018**: System MUST generate random graph topologies with configurable number of internal nodes
- **FR-019**: System MUST accept random seed parameter for deterministic results
- **FR-020**: System MUST accept iteration count parameter (default 2000)
- **FR-021**: System MUST accept max internal nodes parameter (default 2)
- **FR-022**: System MUST evaluate each graph topology using Laplacian method (FR-003 to FR-007)

#### Error Metrics

- **FR-023**: System MUST calculate absolute error: error_abs = |C_eq - C_target|
- **FR-024**: System MUST calculate relative error: error_rel = (|C_eq - C_target| / C_target) × 100%
- **FR-025**: System MUST accept tolerance threshold parameter (default ±5%)
- **FR-026**: System MUST indicate which solutions are within tolerance
- **FR-027**: System MUST handle division by zero when target capacitance is zero (set relative error to infinity or N/A)

#### User Interface

- **FR-028**: System MUST provide input field for target capacitance with tooltip explaining accepted formats
- **FR-029**: System MUST provide editable table for capacitor inventory with add/remove functionality
- **FR-030**: System MUST provide method selection dropdown: "SP Exhaustive", "Heuristic Graph Search"
- **FR-031**: System MUST provide parameter inputs for heuristic method: iterations, max internal nodes, seed
- **FR-032**: System MUST provide tolerance threshold input (percentage)
- **FR-033**: System MUST display results in sortable table showing: topology, C_eq, absolute error, relative error, tolerance status
- **FR-034**: System MUST show progress bar for operations exceeding 1 second with descriptive text
- **FR-035**: System MUST display warning "N>8 may be slow; consider Heuristic method" when SP exhaustive selected with N>8
- **FR-036**: System MUST render circuit diagrams using SchemDraw for SP topologies
- **FR-037**: System MUST render graph diagrams using NetworkX for general topologies
- **FR-038**: System MUST label all diagram components with names and values (e.g., "C1=5.2pF")
- **FR-039**: System MUST label diagram terminals as A and B
- **FR-040**: System MUST provide expanders with theory explanations for each method
- **FR-041**: System MUST render formulas using LaTeX in theory sections
- **FR-042**: System MUST provide tooltips for all input widgets explaining purpose, format, and constraints
- **FR-043**: System MUST maintain unique keys for all widgets to prevent session state loss
- **FR-044**: System MUST cache expensive computations with stable inputs using st.cache_data

#### Presets and Convenience

- **FR-045**: System MUST provide preset buttons to load standard capacitor series (E12, E24, E48, E96)
- **FR-046**: System MUST allow users to filter results to show only solutions within tolerance

#### State Management

- **FR-047**: System MUST persist capacitor inventory in session state across page interactions
- **FR-048**: System MUST persist method selection and parameters in session state
- **FR-049**: System MUST persist last search results in session state

### Key Entities

- **Target Capacitance**: The desired equivalent capacitance value user wants to achieve, specified in Farads (with unit parsing support)
- **Capacitor**: Individual component with a capacitance value in Farads, part of user's available inventory
- **Topology**: Network structure describing how capacitors are connected (series, parallel, or general graph)
- **SP Node**: Recursive data structure representing series-parallel trees (Leaf, Series, or Parallel nodes)
- **Solution**: A topology with its calculated equivalent capacitance, absolute error, relative error, and tolerance status
- **Graph Network**: General network with nodes (terminals A, B plus internal nodes) and edges (capacitors connecting nodes)
- **Error Metric**: Calculated difference between topology's equivalent capacitance and target (absolute and relative)
- **Tolerance**: Acceptable percentage deviation from target capacitance (±%)
- **Method**: Algorithm selection (SP Exhaustive or Heuristic Graph Search)
- **Progress Callback**: Function signature for reporting computation progress to UI

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can enter capacitor values in at least 6 different format combinations (unit suffixes, scientific notation, decimals) and system correctly parses all without errors
- **SC-002**: Users can find all series-parallel solutions for 5 capacitors in under 3 seconds
- **SC-003**: Users can find heuristic solutions with 2000 iterations in under 10 seconds
- **SC-004**: System displays progress feedback for any operation exceeding 1 second
- **SC-005**: 95% of computations complete without crashes or unhandled exceptions
- **SC-006**: All circuit diagrams render with correctly labeled components and terminals
- **SC-007**: Users can identify solutions within tolerance in under 5 seconds by visual scanning of results table
- **SC-008**: System correctly calculates equivalent capacitance for at least 20 test cases covering series, parallel, bridge, and disconnected networks
- **SC-009**: Theory explanations are comprehensible to engineering students (verified by user testing or educational feedback)
- **SC-010**: Users can complete a full workflow (enter target, add capacitors, select method, view results, examine diagrams) in under 2 minutes for typical cases
- **SC-011**: Same heuristic search with same seed produces identical results across multiple runs (determinism)
- **SC-012**: System handles edge cases (zero target, negative values, empty inventory, singular matrices, disconnected networks) without crashing and with clear error messages

## Assumptions

1. **Target Users**: Engineering students, practicing electrical engineers, hobbyists with basic circuit theory knowledge
2. **Browser Environment**: Modern browsers with JavaScript enabled (Chrome, Firefox, Edge, Safari latest versions)
3. **Performance Expectations**: Standard web application responsiveness; operations under 1 second feel instant, 1-5 seconds tolerable with progress feedback
4. **Mathematical Precision**: Double precision floating point (IEEE 754) is sufficient; no arbitrary precision required
5. **Capacitor Value Range**: Typical electronic components from 1fF to 1F; extreme values outside this range may behave unexpectedly
6. **Network Size**: Practical limit of ~20 capacitors for heuristic search; SP exhaustive limited to N≤8 due to combinatorial explosion
7. **Diagram Rendering**: SchemDraw and NetworkX provide sufficient visual clarity; no custom circuit drawing engine required
8. **Session Persistence**: Browser session storage is sufficient; no database or cross-session persistence needed for MVP
9. **Deployment**: Streamlit cloud or local deployment; no complex infrastructure required
10. **Internationalization**: English-only interface for MVP; no multi-language support required initially

## Out of Scope

- **Export Features**: Exporting results to PDF, CSV, or netlist formats (future enhancement)
- **Saved Workspaces**: Persisting inventories and searches across browser sessions (future enhancement)
- **Advanced Heuristics**: Genetic algorithms, simulated annealing, particle swarm optimization (placeholders exist, implementation is future roadmap)
- **Real Component Libraries**: Integration with manufacturer databases (Murata, Kemet, etc.) for real component selection (future enhancement)
- **Tolerance Stacking**: Accounting for component tolerances (±5%, ±10%) in solution feasibility (future enhancement)
- **Multi-objective Optimization**: Minimizing component count, cost, or physical size alongside error (future enhancement)
- **Interactive Circuit Editing**: Drag-and-drop circuit editor for manual topology creation (future enhancement)
- **API/CLI Interface**: Programmatic access or command-line tool (future consideration)
- **Mobile Optimization**: Responsive design for mobile devices is not prioritized for MVP (desktop-first)
- **Real-time Collaboration**: Multiple users editing same workspace (future enhancement)
- **Undo/Redo Functionality**: For inventory edits or parameter changes (future enhancement)

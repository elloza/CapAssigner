# Feature Specification: Professional Circuit Visualization with Lcapy

**Feature ID**: `006-lcapy-visualization`  
**Status**: Draft  
**Created**: 2025-12-12  
**Priority**: P2 (Quality Improvement)

---

## Overview

Replace the current matplotlib/schemdraw-based circuit visualization with **lcapy**, a professional circuit drawing library that generates high-quality diagrams using CircuiTikZ. This will provide cleaner, more professional circuit diagrams for both Series-Parallel (SP) tree topologies and general graph topologies.

### Current Problem

The existing visualization system has several issues:

1. **SP Tree Diagrams (schemdraw)**: 
   - Parallel branches don't always connect properly to terminals
   - Layout can be messy with nested parallel structures
   - Manual positioning logic is complex and error-prone

2. **Graph Diagrams (matplotlib)**:
   - Parallel edges (multiple capacitors between same nodes) are difficult to visualize clearly
   - Requires custom drawing code for capacitor symbols
   - Not professional-looking for technical documentation
   - Layout doesn't always represent electrical connectivity clearly

3. **General Issues**:
   - Two separate rendering systems (schemdraw for SP, matplotlib for graphs)
   - Code duplication and maintenance burden
   - Inconsistent visual style between SP and graph diagrams

### Proposed Solution

Integrate **lcapy** (https://lcapy.readthedocs.io) as the unified visualization library:

- **Lcapy** is a symbolic circuit analysis library with professional schematic generation
- Uses CircuiTikZ backend for publication-quality diagrams
- Native support for series/parallel circuit construction
- Handles complex topologies with automatic layout
- Consistent, professional appearance
- Can export to multiple formats (PNG, PDF, SVG)

---

## User Stories

### US1: Professional SP Circuit Diagrams (Priority: P1)

**As a** user analyzing capacitor networks  
**I want** clean, professional series-parallel circuit diagrams  
**So that** I can understand the topology and share results in technical documentation

**Acceptance Criteria:**
- SP tree topologies render with proper series/parallel layout
- All capacitor values displayed with correct units (pF, nF, µF)
- Terminals A and B clearly labeled
- All connections properly joined (no floating wires)
- Diagram quality suitable for technical reports

**Example:**
```
Input: Series(C1=10µF, Parallel(C2=5µF, C3=5µF))
Output: Professional circuit diagram with C1 in series with (C2 || C3)
```

### US2: Clear Graph Topology Visualization (Priority: P1)

**As a** user working with complex graph topologies  
**I want** clear visualization of multigraph circuits with internal nodes  
**So that** I can understand the structure of SP-reducible graphs

**Acceptance Criteria:**
- All capacitors (edges) displayed, including parallel edges
- Internal nodes clearly marked and positioned
- Terminals A and B distinguished from internal nodes
- Parallel capacitors (multiple edges between same nodes) clearly visible
- Capacitance values labeled on each component

**Example:**
```
Input: Graph with 4 capacitors, 1 internal node, terminals A and B
Output: Circuit with all 4 capacitors visible, internal node labeled
```

### US3: Unified Rendering System (Priority: P2)

**As a** developer maintaining the codebase  
**I want** a single rendering system for all circuit types  
**So that** code is simpler, more maintainable, and visually consistent

**Acceptance Criteria:**
- Single library (lcapy) handles both SP and graph topologies
- Consistent visual style across all circuit types
- Reduced code complexity in plots.py
- Easier to add new visualization features

---

## Functional Requirements

### FR-001: Lcapy Integration
- **Description**: Install and integrate lcapy library into the project
- **Details**: 
  - Add `lcapy` to requirements.txt and environment.yml
  - Verify compatibility with existing dependencies
  - Handle graceful degradation if lcapy installation fails

### FR-002: SP Tree to Lcapy Conversion
- **Description**: Convert SPNode structures to lcapy Circuit syntax
- **Details**:
  - Implement `_sp_to_lcapy(node: SPNode) -> str` function
  - Generate lcapy netlist from Leaf, Series, Parallel nodes
  - Assign unique node labels for series/parallel junctions
  - Include capacitor values with proper units

### FR-003: Graph Topology to Lcapy Conversion
- **Description**: Convert GraphTopology structures to lcapy Circuit syntax
- **Details**:
  - Implement `_graph_to_lcapy(topology: GraphTopology) -> str` function
  - Map NetworkX graph nodes to lcapy nodes
  - Map edges to capacitor components with values
  - Handle MultiGraph parallel edges correctly
  - Label terminals A and B appropriately

### FR-004: Render SP Circuits with Lcapy
- **Description**: Replace `render_sp_circuit()` implementation to use lcapy
- **Details**:
  - Convert SPNode to lcapy circuit
  - Generate schematic diagram
  - Return matplotlib Figure for display in Streamlit
  - Maintain existing function signature for compatibility

### FR-005: Render Graph Circuits with Lcapy
- **Description**: Replace `render_graph_network()` implementation to use lcapy
- **Details**:
  - Convert GraphTopology to lcapy circuit
  - Generate schematic diagram with internal nodes
  - Handle parallel edges (multiple capacitors between same nodes)
  - Return matplotlib Figure for Streamlit display

### FR-006: Fallback to Existing Rendering
- **Description**: If lcapy is unavailable, fall back to current rendering
- **Details**:
  - Check for lcapy availability at import time
  - Use existing schemdraw/matplotlib if lcapy not installed
  - Log warning if fallback is used
  - No functionality loss for users without lcapy

---

## Success Criteria

### SC-001: Visual Quality Improvement
- Circuit diagrams look professional and publication-ready
- All connections properly formed (no floating wires)
- Capacitor symbols follow standard electrical conventions
- Labels clear and unambiguous

### SC-002: All Topologies Supported
- All existing SP tree topologies render correctly
- All graph topologies with internal nodes render correctly
- Parallel edges (MultiGraph) handled properly
- At least 10 test cases covering various topologies

### SC-003: No Regression
- All existing tests pass
- Streamlit app renders circuits without errors
- Export functionality (LaTeX code) still works
- Performance acceptable (< 2 seconds per diagram)

### SC-004: Code Quality
- Reduced code complexity in plots.py (fewer lines)
- Single rendering pathway for all circuit types
- Clear documentation of lcapy integration
- Type hints and docstrings maintained

---

## Non-Goals

- **Circuit simulation**: Lcapy can do analysis, but we only need visualization
- **Interactive diagrams**: Static images sufficient for current use case
- **Animation**: Not needed for this feature
- **3D visualization**: 2D schematics are sufficient
- **Editing circuits visually**: Diagrams are output-only

---

## Technical Considerations

### Dependencies

**Lcapy Requirements:**
- Python ≥ 3.7
- LaTeX with CircuiTikZ (for rendering)
- Alternatively: can use matplotlib backend (no LaTeX needed)

**Integration Approach:**
- Use lcapy's matplotlib backend (no LaTeX required for users)
- Graceful fallback to existing rendering if lcapy unavailable
- Optional: Enable CircuiTikZ/PDF export for users with LaTeX

### Migration Strategy

**Phase 1: Parallel Implementation**
- Add lcapy rendering alongside existing code
- Feature flag to switch between renderers
- Test extensively with existing circuits

**Phase 2: Switch Default**
- Make lcapy the default renderer
- Keep old code as fallback

**Phase 3: Cleanup**
- Remove old matplotlib/schemdraw code once stable
- Update documentation

### Risks

1. **LaTeX Dependency**: Lcapy works best with LaTeX
   - **Mitigation**: Use matplotlib backend, no LaTeX needed
   
2. **Learning Curve**: Team needs to learn lcapy syntax
   - **Mitigation**: Well-documented, similar to SPICE netlists
   
3. **Breaking Changes**: Diagram appearance will change
   - **Mitigation**: Ensure all connections correct, accept cosmetic differences

---

## Open Questions

1. Should we completely remove schemdraw/matplotlib code or keep as fallback?
   - **Recommendation**: Keep as fallback initially, remove after 2-3 releases

2. Should we enable LaTeX/CircuiTikZ export for users with LaTeX installed?
   - **Recommendation**: Yes, make it optional with auto-detection

3. How to handle node positioning for complex graphs?
   - **Recommendation**: Let lcapy handle automatic layout, add manual override if needed

4. Performance impact of lcapy vs current approach?
   - **Recommendation**: Benchmark with 10-20 circuits, ensure < 2s per render

---

## References

- **Lcapy Documentation**: https://lcapy.readthedocs.io/en/latest/
- **Lcapy Schematics Guide**: https://lcapy.readthedocs.io/en/latest/schematics.html
- **CircuiTikZ Manual**: https://texdoc.org/serve/circuitikz/0
- **Current Implementation**: `capassigner/ui/plots.py`

---

## Acceptance

This feature will be considered complete when:

1. ✅ All 5 functional requirements implemented (FR-001 to FR-005)
2. ✅ All 4 success criteria met (SC-001 to SC-004)
3. ✅ Both user stories validated with real circuit examples
4. ✅ Existing test suite passes without modification
5. ✅ Code review completed and approved

# Implementation Tasks: Lcapy Circuit Visualization

**Feature ID**: `006-lcapy-visualization`  
**Status**: Not Started  
**Estimated Time**: 12-16 hours

---

## Task Execution Rules

1. **Sequential by default**: Tasks must be completed in order unless marked [P] for parallel
2. **TDD approach**: Test tasks must complete before implementation tasks
3. **Phase boundaries**: Complete all tasks in a phase before moving to next phase
4. **Validation checkpoints**: Mark tasks with [X] when complete

---

## Phase 1: Setup & Preparation (1 hour)

### Task 1.1: Verify Environment
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: None

**Actions**:
- Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks`
- Verify lcapy installed in conda environment
- Check lcapy version >= 1.20.0
- Test basic lcapy import: `from lcapy import Circuit`

**Validation**:
```bash
.\.conda\python.exe -c "import lcapy; print(lcapy.__version__)"
# Should output: 1.26 or higher
```

**Files**: None

---

### Task 1.2: Create Test File
**Status**: [ ]  
**Estimate**: 10 min  
**Dependencies**: 1.1

**Actions**:
- Create `tests/unit/test_lcapy_integration.py`
- Add imports and basic structure
- Add pytest skip markers for lcapy availability

**Files**:
- `tests/unit/test_lcapy_integration.py` (NEW)

---

### Task 1.3: Add Lcapy Availability Flag [P]
**Status**: [ ]  
**Estimate**: 5 min  
**Dependencies**: 1.1

**Actions**:
- Add lcapy import check at top of `capassigner/ui/plots.py`
- Create `LCAPY_AVAILABLE` boolean flag
- Handle ImportError gracefully

**Files**:
- `capassigner/ui/plots.py` (MODIFY, lines 1-30)

**Code**:
```python
# After schemdraw imports
try:
    from lcapy import Circuit as LcapyCircuit
    LCAPY_AVAILABLE = True
except ImportError:
    LCAPY_AVAILABLE = False
    LcapyCircuit = None
```

---

### Task 1.4: Update Module Docstring [P]
**Status**: [ ]  
**Estimate**: 5 min  
**Dependencies**: 1.3

**Actions**:
- Update `plots.py` module docstring
- Document lcapy integration and fallback behavior

**Files**:
- `capassigner/ui/plots.py` (MODIFY, docstring)

---

### Task 1.5: Add Type Hints Import [P]
**Status**: [ ]  
**Estimate**: 5 min  
**Dependencies**: None

**Actions**:
- Add `from typing import List, Optional, Tuple` if missing
- Verify all type hints available

**Files**:
- `capassigner/ui/plots.py` (MODIFY, imports)

---

## Phase 2: Helper Function Implementation (1.5 hours)

### Task 2.1: Implement Value Formatting Function
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 1.5

**Actions**:
- Implement `_format_capacitance_for_netlist(value_farads: float) -> str`
- Add magnitude-based unit selection (F, mF, uF, nF, pF)
- Use `.6g` format for clean output
- Add docstring with examples

**Files**:
- `capassigner/ui/plots.py` (MODIFY, add function after existing `_format_capacitance`)

**Contract**: See `contracts/lcapy-rendering.yaml` Contract 5

---

### Task 2.2: Test Value Formatting
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 2.1

**Actions**:
- Add test class `TestCapacitanceFormatting` in `test_lcapy_integration.py`
- Test cases:
  - 1.5e-05 F → "15uF"
  - 3.3e-09 F → "3.3nF"
  - 4.7e-12 F → "4.7pF"
  - 2.2e-03 F → "2.2mF"
  - 1.0 F → "1F"
- Run and verify all pass

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

**Validation**:
```bash
.\.conda\python.exe -m pytest tests/unit/test_lcapy_integration.py::TestCapacitanceFormatting -v
```

---

### Task 2.3: Add Logging Setup [P]
**Status**: [ ]  
**Estimate**: 10 min  
**Dependencies**: 1.3

**Actions**:
- Add `import logging` to `plots.py`
- Create module-level logger: `logger = logging.getLogger(__name__)`

**Files**:
- `capassigner/ui/plots.py` (MODIFY, imports)

---

## Phase 3: SPNode Conversion Implementation (2 hours)

### Task 3.1: Implement Recursive Helper Function
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 2.1

**Actions**:
- Implement `_sp_to_lcapy_netlist()` private recursive function
- Parameters: `node, in_node, out_node, capacitors, labels, next_node_ref, lines`
- Handle three cases: Leaf, Series, Parallel
- Add docstring with algorithm explanation

**Files**:
- `capassigner/ui/plots.py` (MODIFY, add function)

**Contract**: See `contracts/lcapy-rendering.yaml` Contract 1

---

### Task 3.2: Implement Public SPNode Conversion
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: 3.1

**Actions**:
- Implement `sp_to_lcapy_netlist(node, capacitor_labels, capacitor_values) -> str`
- Initialize netlist lines list
- Initialize next_node counter at 2
- Call recursive helper with terminals (1, 0)
- Join lines with newline

**Files**:
- `capassigner/ui/plots.py` (MODIFY, add function)

---

### Task 3.3: Test Single Capacitor Conversion
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: 3.2, 1.2

**Actions**:
- Add test `test_sp_single_capacitor_netlist()`
- Test: `Leaf(0, 1e-05)` → "C1 1 0 10uF"
- Verify exact string match

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

**Validation**:
```bash
.\.conda\python.exe -m pytest tests/unit/test_lcapy_integration.py::test_sp_single_capacitor_netlist -v
```

---

### Task 3.4: Test Series Conversion
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 3.3

**Actions**:
- Add test `test_sp_series_netlist()`
- Test: `Series(Leaf(0, 1e-05), Leaf(1, 5e-06))`
- Verify:
  - Two lines produced
  - "C1 1 2 10uF" present
  - "C2 2 0 5uF" present
  - Internal node is 2

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 3.5: Test Parallel Conversion
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 3.4

**Actions**:
- Add test `test_sp_parallel_netlist()`
- Test: `Parallel(Leaf(0, 1e-05), Leaf(1, 5e-06))`
- Verify:
  - Two lines produced
  - "C1 1 0 10uF" present
  - "C2 1 0 5uF" present
  - Both share same nodes (1, 0)

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 3.6: Test Complex SPNode Conversion
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 3.5

**Actions**:
- Add test `test_sp_complex_netlist()` (Exercise 01 structure)
- Test: `Series(Parallel(Leaf(0), Leaf(1)), Series(Leaf(2), Leaf(3)))`
- Verify:
  - Four lines produced
  - Node numbering correct (1 → 2 → 3 → 0)
  - All capacitors present

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

## Phase 4: Graph Conversion Implementation (2 hours)

### Task 4.1: Implement Graph Conversion Function
**Status**: [ ]  
**Estimate**: 40 min  
**Dependencies**: 2.1

**Actions**:
- Implement `graph_to_lcapy_netlist(topology, capacitor_labels?) -> str`
- Create node mapping: A→1, B→0, internal→2+
- Iterate edges with `keys=True` for MultiGraph
- Handle parallel edges with unique labels (CAB, CAB_1, CAB_2)
- Clean labels (remove special characters)

**Files**:
- `capassigner/ui/plots.py` (MODIFY, add function)

**Contract**: See `contracts/lcapy-rendering.yaml` Contract 2

---

### Task 4.2: Test Simple Graph Conversion
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 4.1, 1.2

**Actions**:
- Add test `test_graph_simple_netlist()`
- Create simple graph: A--[10µF]--B
- Verify: "CAB 1 0 10uF"

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 4.3: Test Graph with Internal Node
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 4.2

**Actions**:
- Add test `test_graph_internal_node_netlist()`
- Create graph: A--C--B (two edges)
- Verify:
  - "CAC 1 2 ..." present
  - "CCB 2 0 ..." present
  - Internal node C mapped to 2

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 4.4: Test Graph with Parallel Edges
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 4.3

**Actions**:
- Add test `test_graph_parallel_edges_netlist()`
- Create MultiGraph with 3 edges between A-B
- Verify:
  - Three lines produced
  - Labels: "CAB", "CAB_1", "CAB_2"
  - All edges connect nodes 1 and 0

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 4.5: Test Exercise 02 Graph (Regression)
**Status**: [ ]  
**Estimate**: 10 min  
**Dependencies**: 4.4

**Actions**:
- Add test using Exercise 02 topology (4 capacitors with internal node)
- Use actual `GraphTopology` from sp_graph_exhaustive
- Verify 4 netlist lines produced

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

## Phase 5: Rendering Integration (3 hours)

### Task 5.1: Update render_sp_circuit Function
**Status**: [ ]  
**Estimate**: 40 min  
**Dependencies**: 3.2, 1.3

**Actions**:
- Modify `render_sp_circuit()` in `plots.py`
- Add try/except block for lcapy rendering
- Call `sp_to_lcapy_netlist()`, create `LcapyCircuit`, call `.draw()`
- Configure draw parameters: `draw_nodes='none'`, `label_values=True`, `style='american'`, `dpi=150`
- On exception, log warning and fall back to schemdraw
- Keep existing schemdraw code as fallback

**Files**:
- `capassigner/ui/plots.py` (MODIFY, function ~lines 200-300)

**Contract**: See `contracts/lcapy-rendering.yaml` Contract 3

---

### Task 5.2: Test SP Circuit Rendering
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 5.1, 1.2

**Actions**:
- Add test `test_render_sp_circuit_lcapy()`
- Test with series and parallel structures
- Verify:
  - Returns matplotlib Figure
  - Has axes
  - No exceptions raised
  - Rendering time < 2 seconds

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 5.3: Update render_graph_network Function
**Status**: [ ]  
**Estimate**: 40 min  
**Dependencies**: 4.1, 1.3

**Actions**:
- Modify `render_graph_network()` in `plots.py`
- Add try/except block for lcapy rendering
- Call `graph_to_lcapy_netlist()`, create `LcapyCircuit`, call `.draw()`
- Configure: `draw_nodes='connections'`, `label_nodes=True`, `label_values=True`, `style='american'`, `dpi=150`
- On exception, log warning and fall back to matplotlib
- Keep existing matplotlib code as fallback

**Files**:
- `capassigner/ui/plots.py` (MODIFY, function ~lines 400-500)

**Contract**: See `contracts/lcapy-rendering.yaml` Contract 4

---

### Task 5.4: Test Graph Network Rendering
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 5.3, 1.2

**Actions**:
- Add test `test_render_graph_network_lcapy()`
- Test with simple and complex graphs
- Verify:
  - Returns matplotlib Figure
  - Has axes
  - No exceptions raised
  - Rendering time < 2 seconds

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

### Task 5.5: Test Fallback Behavior
**Status**: [ ]  
**Estimate**: 40 min  
**Dependencies**: 5.4

**Actions**:
- Add test `test_fallback_to_schemdraw()`
- Mock lcapy to raise exception
- Verify schemdraw fallback works
- Add test `test_fallback_to_matplotlib()`
- Verify matplotlib fallback for graphs

**Files**:
- `tests/unit/test_lcapy_integration.py` (MODIFY)

---

## Phase 6: Visual Validation (2 hours)

### Task 6.1: Create Visual Regression Test Script [P]
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 5.4

**Actions**:
- Create `scripts/visual_regression_test.py`
- Generate diagrams for known exercises
- Save both old (matplotlib) and new (lcapy) versions
- Create side-by-side comparison

**Files**:
- `scripts/visual_regression_test.py` (NEW)

---

### Task 6.2: Test Exercise 01 Visualization
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 6.1, 5.2

**Actions**:
- Run visual regression for Exercise 01
- Verify:
  - All 4 capacitors visible
  - SP structure clear
  - Values labeled correctly
  - Professional appearance

**Files**: None (manual verification)

---

### Task 6.3: Test Exercise 02 Visualization
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 6.2, 5.4

**Actions**:
- Run visual regression for Exercise 02
- Verify:
  - All 4 capacitors visible (BUG FIX VALIDATION)
  - Internal node shown
  - Terminal B connected (BUG FIX VALIDATION)
  - No floating wires

**Files**: None (manual verification)

---

### Task 6.4: Streamlit App Integration Test
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 6.3

**Actions**:
- Start Streamlit app: `streamlit run app.py`
- Test workflow:
  1. Enter 2 capacitors (10µF, 5µF)
  2. Set target 3.33µF
  3. Click "Calculate"
  4. Verify diagram renders
- Test with Exercise 02 values
- Check performance (< 2s)

**Files**: None (manual verification)

---

### Task 6.5: Performance Benchmarking
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 6.4

**Actions**:
- Create benchmark script
- Measure rendering time for:
  - 2 capacitors: < 500ms
  - 5 capacitors: < 1s
  - 10 capacitors: < 2s
  - 20 capacitors: < 5s
- Compare lcapy vs schemdraw/matplotlib

**Files**:
- `scripts/benchmark_rendering.py` (NEW)

---

## Phase 7: Documentation & Cleanup (1.5 hours)

### Task 7.1: Update Function Docstrings
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 5.4

**Actions**:
- Update `render_sp_circuit()` docstring
- Update `render_graph_network()` docstring
- Mention lcapy integration and fallback behavior
- Add examples

**Files**:
- `capassigner/ui/plots.py` (MODIFY, docstrings)

---

### Task 7.2: Add Code Comments
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: 7.1

**Actions**:
- Add inline comments for complex logic
- Explain node numbering convention (A=1, B=0, internal=2+)
- Document fallback strategy

**Files**:
- `capassigner/ui/plots.py` (MODIFY, comments)

---

### Task 7.3: Create Implementation Summary [P]
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 6.5

**Actions**:
- Create `specs/006-lcapy-visualization/IMPLEMENTATION_SUMMARY.md`
- Document:
  - Tasks completed
  - Files modified
  - Test results
  - Performance metrics
  - Visual validation results
  - Known limitations

**Files**:
- `specs/006-lcapy-visualization/IMPLEMENTATION_SUMMARY.md` (NEW)

---

### Task 7.4: Update README [P]
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: 7.3

**Actions**:
- Update `README.md` if circuit visualization mentioned
- Add lcapy to dependencies list
- Update screenshots if present

**Files**:
- `README.md` (MODIFY, optional)

---

### Task 7.5: Update CLAUDE.md [P]
**Status**: [ ]  
**Estimate**: 10 min  
**Dependencies**: 7.3

**Actions**:
- Add feature 006 to development log
- Document lcapy integration completion

**Files**:
- `CLAUDE.md` (MODIFY)

---

## Phase 8: Final Testing & Validation (2 hours)

### Task 8.1: Run Full Unit Test Suite
**Status**: [ ]  
**Estimate**: 10 min  
**Dependencies**: 7.2

**Actions**:
- Run all tests: `pytest tests/unit/ -v`
- Verify all tests pass
- Check code coverage >= 80%

**Validation**:
```bash
.\.conda\python.exe -m pytest tests/unit/ -v --cov=capassigner.ui.plots
```

---

### Task 8.2: Run Contract Tests
**Status**: [ ]  
**Estimate**: 10 min  
**Dependencies**: 8.1

**Actions**:
- Run contract tests: `pytest tests/contract/ -v`
- Verify no regressions in existing contracts

**Validation**:
```bash
.\.conda\python.exe -m pytest tests/contract/ -v
```

---

### Task 8.3: Run Integration Tests
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: 8.2

**Actions**:
- Run integration tests: `pytest tests/integration/ -v`
- Verify end-to-end workflows work

**Validation**:
```bash
.\.conda\python.exe -m pytest tests/integration/ -v
```

---

### Task 8.4: Full Regression Test
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 8.3

**Actions**:
- Run ALL tests: `pytest tests/ -v`
- Verify:
  - 0 failures
  - 0 errors
  - All skipped tests documented

**Validation**:
```bash
.\.conda\python.exe -m pytest tests/ -v
```

---

### Task 8.5: Code Quality Check [P]
**Status**: [ ]  
**Estimate**: 20 min  
**Dependencies**: 8.1

**Actions**:
- Run linter (if configured): `pylint capassigner/ui/plots.py`
- Check type hints: `mypy capassigner/ui/plots.py` (if configured)
- Verify no new warnings

**Files**: None

---

### Task 8.6: Verify Success Criteria
**Status**: [ ]  
**Estimate**: 30 min  
**Dependencies**: 8.4, 6.5

**Actions**:
- Review `spec.md` success criteria
- Verify each criterion met:
  - **SC-001**: Diagrams professional ✓
  - **SC-002**: All topologies supported ✓
  - **SC-003**: No regressions ✓
  - **SC-004**: Code complexity reduced ✓

**Files**: None (manual checklist)

---

### Task 8.7: Create Release Notes
**Status**: [ ]  
**Estimate**: 15 min  
**Dependencies**: 8.6

**Actions**:
- Create `specs/006-lcapy-visualization/RELEASE_NOTES.md`
- Document:
  - New features
  - Bug fixes (Exercise 02 disconnected terminal)
  - Breaking changes (none expected)
  - Migration guide

**Files**:
- `specs/006-lcapy-visualization/RELEASE_NOTES.md` (NEW)

---

## Task Summary

**Total Tasks**: 48  
**Parallel Tasks**: 7  
**Sequential Tasks**: 41

**Estimated Time by Phase**:
- Phase 1 (Setup): 1 hour
- Phase 2 (Helpers): 1.5 hours
- Phase 3 (SPNode): 2 hours
- Phase 4 (Graph): 2 hours
- Phase 5 (Integration): 3 hours
- Phase 6 (Validation): 2 hours
- Phase 7 (Documentation): 1.5 hours
- Phase 8 (Testing): 2 hours

**Total**: 15 hours

---

## Critical Path

The longest sequential dependency chain:

1.1 → 1.2 → 2.1 → 2.2 → 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6 →  
4.1 → 4.2 → 4.3 → 4.4 → 4.5 →  
5.1 → 5.2 → 5.3 → 5.4 → 5.5 →  
6.2 → 6.3 → 6.4 → 6.5 →  
7.2 → 8.1 → 8.2 → 8.3 → 8.4 → 8.6 → 8.7

**Critical Path Length**: ~13 hours (main sequential work)

---

## Files Modified

**Modified**:
- `capassigner/ui/plots.py` (~10 tasks modify this file)

**Created**:
- `tests/unit/test_lcapy_integration.py` (NEW, ~15 tests)
- `scripts/visual_regression_test.py` (NEW)
- `scripts/benchmark_rendering.py` (NEW)
- `specs/006-lcapy-visualization/IMPLEMENTATION_SUMMARY.md` (NEW)
- `specs/006-lcapy-visualization/RELEASE_NOTES.md` (NEW)

**Updated** (optional):
- `README.md` (if circuit visualization documented)
- `CLAUDE.md` (development log)

---

## Rollback Plan

If implementation fails critically:

1. **Revert commits**: `git revert <commit-hash>`
2. **Fallback guaranteed**: Schemdraw/matplotlib still present
3. **Feature flag**: Set `LCAPY_AVAILABLE = False` to disable
4. **No data loss**: No database or file format changes

---

## Post-Implementation Monitoring

After deployment, monitor:

- User reports of visualization issues
- Performance metrics (rendering time)
- Error logs (fallback frequency)
- Edge cases not covered in tests

**Review after**: 2-3 releases (~1-2 months)

**Decision point**: Remove old rendering code or keep both?

---

## Notes

- **TDD Approach**: Tests written before implementation
- **Incremental**: Small, verifiable steps
- **Reversible**: Can disable with feature flag
- **Validated**: Visual regression and performance checks
- **Documented**: All functions have docstrings and examples


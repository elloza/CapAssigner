# Feature Specification: Exhaustive Graph Enumeration with Internal Nodes

**Feature Branch**: `004-graph-enumeration`  
**Created**: December 12, 2025  
**Status**: ❌ **CANCELLED**  
**Priority**: ~~P2~~ **N/A**  
**Estimated Effort**: ~~2-3 weeks~~ **Saved**  

---

## ⚠️ PROJECT CANCELLED

**Date Cancelled**: December 12, 2025  
**Reason**: Validation experiment proved heuristic search already solves the motivating problem.

**Validation Results**:
- Heuristic search finds classroom 1.0pF solution with **100% success rate**
- Performance: **~3 seconds** (vs estimated 1-2 minutes for exhaustive)
- Works with only **10,000 iterations** and `max_internal_nodes=2`
- Top 5 results **all** achieve 0% error (multiple exact solutions found)

**Conclusion**: Graph exhaustive enumeration is **unnecessary** because:
1. Heuristic already solves the classroom problem perfectly
2. Heuristic is **faster** than exhaustive would be
3. Heuristic is **more scalable** (works for N>10)
4. Saves **3 weeks of development time**

**See**: [VALIDATION_RESULTS_CANCELLED.md](VALIDATION_RESULTS_CANCELLED.md) for full experiment details.

---

## Original Executive Summary (For Reference)

Implement **exhaustive enumeration of general graph topologies** with internal nodes to guarantee finding optimal solutions for circuit problems that cannot be represented as pure series-parallel (SP) trees. This addresses the classroom 4-capacitor problem where SP enumeration fails (7.69% error) because the correct topology requires internal nodes and capacitor value reuse.

**Key Motivation**: While SP enumeration works perfectly for SP-reducible circuits and heuristic search provides probabilistic exploration, there exists a gap for **guaranteed optimal solutions** in small-to-medium sized problems (N≤6, k≤2 internal nodes) where exhaustive search is computationally feasible.

**Tradeoff**: Completeness vs computational cost. This feature is NOT a replacement for SP/heuristic methods, but a **third complementary approach** for users who need guaranteed optimality and can accept longer computation times for small problem instances.

---

## Problem Statement

### Current Limitations

**SP Enumeration**:
- ✅ Fast and optimal for SP-reducible circuits
- ❌ Cannot generate topologies with internal nodes (C, D, E, ...)
- ❌ Cannot reuse capacitor values on multiple edges
- ❌ Fails on bridge circuits, mesh networks, classroom example

**Heuristic Search**:
- ✅ Explores graph topologies with internal nodes
- ✅ Scalable to large N
- ❌ Probabilistic - no guarantee of finding optimal
- ❌ May require many iterations (10k-100k)
- ❌ May miss rare optimal topologies

**Graph Laplacian**:
- ✅ Calculates C_eq for any given topology exactly
- ❌ Requires explicit topology specification
- ❌ Cannot search/enumerate topologies

### Gap to Fill

Users need a method that:
1. **Guarantees finding the optimal solution** (like SP enumeration)
2. **Handles graph topologies with internal nodes** (like heuristic search)
3. **Is computationally tractable** for small-to-medium problems

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guaranteed Classroom Solution (Priority: P1)

A professor uses the system with the classroom 4-capacitor example. SP enumeration returns 7.69% error, and heuristic search (even with 100k iterations) might miss the exact solution due to randomness. The user needs **guaranteed optimal** solution.

**Acceptance Scenarios**:

1. **Given** the classroom example (C₁=2pF, C₂=3pF, C₃=3pF, C₄=1pF, target=1.0pF) with graph enumeration (k=2 internal nodes), **When** the algorithm completes, **Then** it finds the exact 1.0pF topology with C_eq error < 1e-10

2. **Given** N=4 capacitors and k=2 internal nodes, **When** graph enumeration runs, **Then** the number of generated topologies is logged and matches theoretical expectations (accounting for isomorphism elimination)

3. **Given** a small problem instance (N≤5, k≤2), **When** user selects "Graph Exhaustive" method, **Then** the system displays estimated runtime and topology count before starting

### User Story 2 - Bridge Circuit Enumeration (Priority: P2)

A circuit designer needs to find optimal solutions for a Wheatstone bridge configuration with 5 capacitors. SP enumeration cannot represent bridges, and heuristic search is uncertain.

**Acceptance Scenarios**:

1. **Given** 5 capacitors forming a bridge topology requirement, **When** graph enumeration with k=2 internal nodes runs, **Then** bridge topologies are included in the search space

2. **Given** multiple bridge configurations exist in results, **When** viewing solutions, **Then** circuit diagrams correctly display internal nodes C, D and bridge connections

3. **Given** a bridge circuit with exact solution exists, **When** enumeration completes, **Then** the exact solution ranks as best (lowest error)

### User Story 3 - Performance Scaling Awareness (Priority: P1)

A user tries to use graph enumeration with N=8 capacitors and k=3 internal nodes. The system should prevent or warn about computationally infeasible configurations.

**Acceptance Scenarios**:

1. **Given** N>6 or k>2, **When** user selects graph enumeration, **Then** system displays warning: "Graph enumeration may take hours/days for these parameters. Consider heuristic search instead."

2. **Given** user confirms running large enumeration, **When** computation starts, **Then** system displays live progress: "Generating topologies... 1000/~50000 (2%)" with estimated time remaining

3. **Given** enumeration is running, **When** user cancels, **Then** system returns partial results found so far (graceful degradation)

---

## Functional Requirements *(mandatory)*

### FR-001: Graph Topology Generation

**Description**: Generate all possible graph topologies with specified number of internal nodes.

**Inputs**:
- `n_capacitors` (int): Number of capacitor indices available (2-10)
- `n_internal_nodes` (int): Number of internal nodes beyond A, B (0-3)
- `allow_capacitor_reuse` (bool): Whether same capacitor value can appear on multiple edges (default: True)

**Process**:
1. Define node set: {A, B, C, D, ...} where C, D, ... are first k internal nodes
2. Enumerate all possible edge sets connecting nodes
3. For each edge set, enumerate capacitor assignments (with/without reuse)
4. Filter invalid topologies (disconnected, A-B not connected, etc.)
5. Eliminate isomorphic duplicates

**Outputs**:
- Iterator/generator yielding `GraphTopology` objects
- Each object contains: nodes, edges, capacitor assignments, topology hash

**Constraints**:
- Must support NetworkX graph representation
- Must integrate with existing `calculate_graph_ceq()` function
- Must handle self-loops (edges A-A) rejection
- Must validate that A and B are in graph

**Non-Functional**:
- Should use **generator pattern** to avoid memory explosion
- Should support **early termination** if user-defined conditions met (e.g., found exact solution)
- Should cache/memoize topology checks where possible

### FR-002: Isomorphism Filtering

**Description**: Eliminate duplicate topologies that are graph-isomorphic (same structure, different labeling).

**Rationale**: Many generated graphs are structurally identical but with different node labels (e.g., C↔D swap). Isomorphism detection reduces search space by 10-100x.

**Inputs**:
- `GraphTopology` object with nodes, edges, capacitor assignments

**Process**:
1. Compute canonical graph representation (ignoring internal node labels)
2. Use NetworkX `graph_hash()` or `vf2` isomorphism algorithm
3. Maintain hash table of seen canonical forms
4. Keep first instance of each canonical form, discard duplicates

**Outputs**:
- Boolean: is_duplicate
- If not duplicate, add to hash table

**Constraints**:
- Must preserve A, B terminal identity (A and B are **not** interchangeable)
- Internal nodes C, D, E **are** interchangeable (symmetry breaking)
- Edge capacitor values matter for equivalence

**Performance**:
- Target: <10ms per topology for isomorphism check
- Use hash-based fast rejection before expensive graph isomorphism

### FR-003: Topology Validation

**Description**: Validate that generated graphs represent valid electrical circuits.

**Validation Rules**:
1. **Connectivity**: A and B must be connected via some path
2. **No self-loops**: No edge connects node to itself
3. **Simple graph**: At most one edge between any pair of nodes (parallel edges merged)
4. **Non-trivial**: At least 1 edge (more realistically, at least n_capacitors edges)
5. **Feasible**: Number of edges must allow capacitor assignment

**Inputs**: Graph structure (nodes, edges)

**Outputs**: Boolean valid, string reason (if invalid)

### FR-004: Integration with Existing Core

**Description**: Graph enumeration must integrate seamlessly with existing modules.

**Integration Points**:

1. **calculate_graph_ceq()** in `capassigner/core/graphs.py`
   - Each enumerated topology is evaluated using this function
   - Returns (ceq, warning) tuple

2. **Solution** dataclass in `capassigner/core/metrics.py`
   - Graph topologies wrapped in Solution objects
   - Include topology representation (NetworkX graph + node positions)

3. **find_best_graph_exhaustive_solutions()** in new `graph_enumeration.py`
   - Similar API to `find_best_sp_solutions()` and `find_best_heuristic_solutions()`
   - Returns list of Solution objects ranked by error

**API Signature**:
```python
def find_best_graph_exhaustive_solutions(
    capacitors: List[float],
    target_ceq: float,
    n_internal_nodes: int = 1,
    allow_capacitor_reuse: bool = True,
    top_k: int = 10,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    max_time_seconds: Optional[float] = None
) -> List[Solution]:
    """
    Exhaustively enumerate graph topologies with internal nodes.
    
    Args:
        capacitors: List of capacitor values in Farads
        target_ceq: Target equivalent capacitance in Farads
        n_internal_nodes: Number of internal nodes (0-3)
        allow_capacitor_reuse: If True, same capacitor value can appear multiple times
        top_k: Number of best solutions to return
        progress_callback: Optional callback(current, estimated_total)
        max_time_seconds: Optional time limit for enumeration
        
    Returns:
        List of Solution objects ranked by error
        
    Raises:
        ValueError: If n_internal_nodes > 3 or len(capacitors) > 10
        TimeoutError: If max_time_seconds exceeded
    """
```

### FR-005: Performance Estimation

**Description**: Estimate computational cost before running enumeration.

**Formula**:
```
Estimated topologies ≈ C(N+k, 2) * (n^m) / symmetry_factor
```
Where:
- N = number of capacitor types
- k = number of internal nodes
- C(N+k, 2) = possible edges between N+k nodes
- n^m = capacitor assignments
- symmetry_factor ≈ k! (internal node permutations)

**Outputs**:
- Estimated topology count (integer)
- Estimated time (seconds, based on benchmark: ~1000 topologies/sec)
- Feasibility level: "Fast (<1min)", "Moderate (1-10min)", "Slow (10min-1hr)", "Infeasible (>1hr)"

**UI Integration**:
- Display before starting enumeration
- Allow user to confirm or cancel
- For "Infeasible" cases, block execution and suggest heuristic search

---

## Non-Functional Requirements

### NFR-001: Performance Targets

| Configuration | Estimated Topologies | Target Time | Status |
|---------------|---------------------|-------------|---------|
| N=4, k=1 | ~1,000 | <10 seconds | ✅ Feasible |
| N=4, k=2 | ~10,000 | 1-2 minutes | ✅ Feasible |
| N=5, k=2 | ~100,000 | 10-20 minutes | ⚠️ Borderline |
| N=6, k=2 | ~500,000 | 1-2 hours | ❌ Slow |
| N=8, k=3 | >10,000,000 | Days | ❌ Infeasible |

**Constraints**:
- Hard limit: N ≤ 10, k ≤ 3
- Recommended: N ≤ 5, k ≤ 2
- Warning threshold: Estimated topologies > 50,000

### NFR-002: Memory Efficiency

**Requirements**:
- Use **generator pattern** - do not materialize all topologies in memory
- Stream topologies through evaluation pipeline
- Maintain only top-k solutions in memory (heap-based priority queue)

**Rationale**: For N=5, k=2, materializing all 100k topologies would use ~500MB RAM. Generator approach uses O(1) memory.

### NFR-003: Progress Reporting

**Requirements**:
- Display progress bar with percentage (if total count estimable)
- Display "Topologies evaluated: X" (even if total unknown)
- Display current best solution (C_eq, error) as search progresses
- Estimated time remaining (based on average topology evaluation time)

**UI Integration**:
- Streamlit progress bar
- Live-updating metrics (st.empty() containers)
- Cancel button (st.stop() on user request)

### NFR-004: Graceful Degradation

**Scenarios**:

1. **User cancellation**: Return best solutions found so far
2. **Time limit exceeded**: Return best solutions found, log warning
3. **Memory pressure**: Reduce top_k, discard lower-ranked solutions
4. **Invalid topology**: Log warning, skip, continue enumeration

---

## Algorithm Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│  find_best_graph_exhaustive_solutions()                 │
│  - Validate inputs (N, k)                               │
│  - Estimate computational cost                          │
│  - Initialize topology generator                        │
└────────────────┬────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│  GraphTopologyGenerator                                 │
│  - generate_node_sets(k)                                │
│  - enumerate_edge_sets(nodes)                           │
│  - assign_capacitors(edges, capacitors, reuse)          │
└────────────────┬────────────────────────────────────────┘
                 │
                 v (iterator)
┌─────────────────────────────────────────────────────────┐
│  IsomorphismFilter                                      │
│  - compute_canonical_hash(topology)                     │
│  - check_duplicate(hash_table)                          │
│  - filter unique topologies                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 v (filtered iterator)
┌─────────────────────────────────────────────────────────┐
│  TopologyValidator                                      │
│  - check_connectivity(A, B)                             │
│  - validate_structure()                                 │
│  - reject invalid topologies                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 v (valid topologies)
┌─────────────────────────────────────────────────────────┐
│  EvaluationPipeline                                     │
│  - calculate_graph_ceq(topology) [existing function]    │
│  - compute_error(ceq, target)                           │
│  - create Solution object                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 v
┌─────────────────────────────────────────────────────────┐
│  SolutionRanker (Top-K Heap)                            │
│  - maintain heap of top-k solutions                     │
│  - discard worse solutions                              │
│  - return sorted list at end                            │
└─────────────────────────────────────────────────────────┘
```

### Detailed Algorithm Steps

#### Step 1: Node Set Generation

```python
def generate_node_sets(n_internal: int) -> List[str]:
    """Generate node labels: A, B (terminals) + C, D, E, ... (internal)."""
    terminals = ['A', 'B']
    internal = [chr(ord('C') + i) for i in range(n_internal)]
    return terminals + internal
```

**Example**:
- k=0 → ['A', 'B']
- k=1 → ['A', 'B', 'C']
- k=2 → ['A', 'B', 'C', 'D']

#### Step 2: Edge Set Enumeration

**Challenge**: For k nodes, there are C(k, 2) = k*(k-1)/2 possible edges. We need to enumerate all subsets.

**Approach**: Use bitmask or itertools.combinations

```python
from itertools import combinations, chain

def enumerate_edge_sets(nodes: List[str], min_edges: int = 1) -> Iterator[List[Tuple[str, str]]]:
    """
    Enumerate all possible edge sets connecting nodes.
    
    Args:
        nodes: List of node labels
        min_edges: Minimum number of edges (default 1)
        
    Yields:
        Lists of (node_i, node_j) tuples representing edges
    """
    all_possible_edges = list(combinations(nodes, 2))  # All pairs
    
    # Enumerate all subsets of edges (power set)
    for r in range(min_edges, len(all_possible_edges) + 1):
        for edge_set in combinations(all_possible_edges, r):
            # Filter: must form connected graph with A-B path
            if is_connected_with_path(edge_set, 'A', 'B'):
                yield list(edge_set)
```

**Optimization**: Early rejection of disconnected graphs saves evaluation time.

#### Step 3: Capacitor Assignment

**Without Reuse** (each capacitor index used once):
```python
from itertools import permutations

def assign_capacitors_no_reuse(edges, capacitor_indices):
    """Assign each capacitor index to edges (permutations)."""
    n_edges = len(edges)
    n_caps = len(capacitor_indices)
    
    if n_edges > n_caps:
        return  # Cannot assign (not enough capacitors)
    
    # Use first n_edges capacitors, try all permutations
    for perm in permutations(capacitor_indices[:n_edges]):
        yield dict(zip(edges, perm))
```

**With Reuse** (capacitor values can repeat):
```python
from itertools import product

def assign_capacitors_with_reuse(edges, capacitor_values):
    """Assign capacitor values to edges (with repetition)."""
    n_edges = len(edges)
    
    # Cartesian product: each edge can have any capacitor value
    for assignment in product(capacitor_values, repeat=n_edges):
        yield dict(zip(edges, assignment))
```

**Complexity**:
- Without reuse: O(n!) permutations
- With reuse: O(n^m) assignments (n capacitors, m edges)

**Optimization**: For classroom example, with reuse is essential (3pF appears 3 times).

#### Step 4: Isomorphism Filtering

**Goal**: Eliminate topologically identical graphs with different internal node labels.

**Approach**: Use NetworkX graph hashing with node attribute preservation for terminals.

```python
import networkx as nx
from networkx.algorithms import isomorphism

def compute_canonical_hash(graph: nx.Graph) -> str:
    """
    Compute canonical hash for graph considering:
    - A and B are fixed terminals (not interchangeable)
    - Internal nodes are interchangeable
    - Edge capacitor values matter
    """
    # Create node-attributed graph for hashing
    # Mark terminals with special attribute
    node_attrs = {node: {'terminal': node in ['A', 'B']} for node in graph.nodes()}
    nx.set_node_attributes(graph, node_attrs)
    
    # Use Weisfeiler-Lehman graph hash
    return nx.weisfeiler_lehman_graph_hash(graph, node_attr='terminal', edge_attr='capacitance')

class IsomorphismFilter:
    def __init__(self):
        self.seen_hashes = set()
    
    def is_duplicate(self, graph: nx.Graph) -> bool:
        """Check if graph is isomorphic to previously seen topology."""
        canonical_hash = compute_canonical_hash(graph)
        
        if canonical_hash in self.seen_hashes:
            return True
        
        self.seen_hashes.add(canonical_hash)
        return False
```

**Performance**: Hashing is O(n log n), much faster than full isomorphism check O(n!).

#### Step 5: Connectivity Validation

```python
def is_connected_with_path(edges: List[Tuple[str, str]], start: str, end: str) -> bool:
    """Check if edges form connected graph with path from start to end."""
    G = nx.Graph()
    G.add_edges_from(edges)
    
    if start not in G or end not in G:
        return False
    
    return nx.has_path(G, start, end)
```

**Early rejection**: Skip edge sets that don't connect A to B (saves capacitor assignment enumeration).

#### Step 6: Evaluation Pipeline

```python
def evaluate_topology(graph: nx.Graph, target_ceq: float) -> Solution:
    """Evaluate topology and create Solution object."""
    # Use existing function from graphs.py
    ceq, warning = calculate_graph_ceq(graph, terminal_a='A', terminal_b='B')
    
    # Calculate error
    error = abs(ceq - target_ceq) / target_ceq if target_ceq != 0 else float('inf')
    
    # Create Solution object
    return Solution(
        topology=graph,  # Store graph for visualization
        ceq=ceq,
        error=error,
        warning=warning,
        method="graph_exhaustive"
    )
```

#### Step 7: Top-K Heap Maintenance

```python
import heapq

class TopKSolutions:
    def __init__(self, k: int):
        self.k = k
        self.heap = []  # Min-heap of (-error, solution)
    
    def add(self, solution: Solution):
        """Add solution, maintaining top-k by error."""
        # Negate error for max-heap behavior
        heapq.heappush(self.heap, (-solution.error, solution))
        
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)  # Remove worst
    
    def get_sorted(self) -> List[Solution]:
        """Return solutions sorted by error (best first)."""
        return [sol for _, sol in sorted(self.heap, key=lambda x: -x[0])]
```

**Memory**: O(k) instead of O(total_topologies).

---

## Implementation Plan

### Phase 1: Core Algorithm (Week 1)

**Files to Create**:
1. `capassigner/core/graph_enumeration.py` - Main enumeration logic
2. `tests/unit/test_graph_enumeration.py` - Comprehensive tests

**Deliverables**:
- [ ] T001: Implement `generate_node_sets()`
- [ ] T002: Implement `enumerate_edge_sets()` with connectivity check
- [ ] T003: Implement `assign_capacitors_no_reuse()`
- [ ] T004: Implement `assign_capacitors_with_reuse()`
- [ ] T005: Integrate with `calculate_graph_ceq()` from graphs.py
- [ ] T006: Create `GraphTopologyGenerator` class with iterator interface
- [ ] T007: Unit tests for each component (10+ tests)

**Success Criteria**:
- Generator yields valid topologies for N=3, k=1 (simple case)
- All tests passing
- Generates expected count of topologies (validate against hand calculation)

### Phase 2: Isomorphism & Optimization (Week 2, Days 1-3)

**Files to Modify**:
- `capassigner/core/graph_enumeration.py` - Add filtering

**Deliverables**:
- [ ] T008: Implement `compute_canonical_hash()` using NetworkX
- [ ] T009: Implement `IsomorphismFilter` class with hash table
- [ ] T010: Add isomorphism filtering to generator pipeline
- [ ] T011: Benchmark isomorphism detection performance
- [ ] T012: Test duplicate elimination (verify no false positives/negatives)

**Success Criteria**:
- Topology count reduced by 5-10x after isomorphism filtering
- No false duplicates (manually verified for small cases)
- Performance <10ms per topology check

### Phase 3: API & Integration (Week 2, Days 4-5)

**Files to Modify**:
- `capassigner/core/graph_enumeration.py` - Add main API function
- `capassigner/core/metrics.py` - Extend Solution dataclass if needed

**Deliverables**:
- [ ] T013: Implement `find_best_graph_exhaustive_solutions()` API
- [ ] T014: Add progress callback support
- [ ] T015: Add time limit (max_time_seconds) with graceful termination
- [ ] T016: Implement `estimate_computational_cost()` function
- [ ] T017: Integration tests with classroom example
- [ ] T018: Validate classroom example finds 1.0pF exactly

**Success Criteria**:
- Classroom example (N=4, k=2) finds C_eq=1.0pF with error <1e-10
- API matches existing SP/heuristic function signatures
- Progress callback fires at reasonable intervals

### Phase 4: UI Integration (Week 3, Days 1-2)

**Files to Modify**:
- `capassigner/ui/pages.py` - Add "Graph Exhaustive" method option
- `capassigner/ui/plots.py` - Ensure graph topologies visualize correctly
- `capassigner/ui/tooltips.py` - Add explanations and warnings

**Deliverables**:
- [ ] T019: Add "Graph Exhaustive" radio button to method selection
- [ ] T020: Display estimated cost before starting
- [ ] T021: Show confirmation dialog for slow configurations
- [ ] T022: Display progress bar during enumeration
- [ ] T023: Visualize graph topologies with internal nodes (SchemDraw/NetworkX)
- [ ] T024: Add theory section explaining graph enumeration

**Success Criteria**:
- User can select and run graph exhaustive method
- Progress updates visible in UI
- Circuit diagrams show internal nodes correctly
- Warnings display for N>5 or k>2

### Phase 5: Documentation & Polish (Week 3, Days 3-5)

**Files to Create/Modify**:
- `specs/004-graph-enumeration/research.md` - Algorithm analysis
- `README.md` - Add graph exhaustive method documentation
- `capassigner/ui/theory.py` - Add graph enumeration theory

**Deliverables**:
- [ ] T025: Write comprehensive docstrings (Google style)
- [ ] T026: Add algorithm theory to UI (formulas, complexity, when to use)
- [ ] T027: Update README with graph exhaustive method
- [ ] T028: Create performance benchmarks (N=3,4,5 × k=1,2)
- [ ] T029: Add examples to documentation
- [ ] T030: Code review and refactoring

**Success Criteria**:
- All functions fully documented
- User guide explains when to use each method
- Performance benchmarks published
- Code passes linting/type checking

---

## Risks & Mitigations

### Risk 1: Computational Explosion

**Risk**: For N=6, k=2, enumeration takes hours and overwhelms system.

**Mitigation**:
- Hard limits on N and k
- Estimate cost before running
- Require user confirmation for slow configs
- Implement time limits and graceful cancellation
- Use generator pattern to avoid memory issues

### Risk 2: Isomorphism Detection Incorrect

**Risk**: False positives (different topologies marked as duplicate) or false negatives (duplicates not detected).

**Mitigation**:
- Extensive testing with known cases
- Manual verification for N=3, k=1 (small enough to enumerate by hand)
- Use well-tested NetworkX isomorphism algorithms
- Validate that terminal nodes A, B are handled correctly

### Risk 3: Integration Complexity

**Risk**: Graph enumeration doesn't integrate cleanly with existing codebase.

**Mitigation**:
- Match API signature of existing `find_best_*_solutions()` functions
- Reuse `calculate_graph_ceq()` without modification
- Extend Solution dataclass minimally (add graph storage)
- Comprehensive integration tests

### Risk 4: User Expectations Mismatch

**Risk**: Users expect graph exhaustive to be fast like SP enumeration.

**Mitigation**:
- Clear UI warnings about performance
- Display estimated time before starting
- Recommend heuristic search for N>5
- Add theory section explaining tradeoffs

---

## Success Metrics

### Functional Correctness

- [ ] Classroom example (N=4, k=2) finds C_eq=1.0pF exactly
- [ ] Bridge circuit (N=5, k=2) finds optimal topology
- [ ] All generated topologies are valid (connected, A-B path)
- [ ] No duplicate topologies in results (isomorphism filtering works)
- [ ] Integration tests pass (100% coverage of main API)

### Performance

- [ ] N=4, k=1: <10 seconds
- [ ] N=4, k=2: <2 minutes
- [ ] N=5, k=2: <20 minutes
- [ ] Isomorphism check: <10ms per topology
- [ ] Memory usage: <100MB for N=5, k=2

### Usability

- [ ] Clear UI warnings for slow configurations
- [ ] Progress bar updates smoothly
- [ ] User can cancel enumeration at any time
- [ ] Theory section explains when to use graph exhaustive
- [ ] Error messages are helpful and actionable

---

## Out of Scope (Future Enhancements)

The following are explicitly **not** part of this initial implementation:

1. **Parallel/Distributed Enumeration**: Running enumeration across multiple cores/machines
2. **Smart Pruning**: Using circuit theory to prune topology space beyond connectivity
3. **Delta-Wye Transformations**: Applying transformations to reduce search space
4. **Capacitor Value Optimization**: Finding optimal capacitor values (not just topologies)
5. **N>10 or k>3**: These are computationally infeasible even with optimizations
6. **GPU Acceleration**: Offloading graph operations to GPU
7. **Incremental Enumeration**: Caching results for progressive refinement

---

## Dependencies

**New Dependencies** (to add to requirements.txt):
- NetworkX already present (used for graph operations)
- No new external dependencies required

**Existing Dependencies**:
- `capassigner.core.graphs.calculate_graph_ceq()` - Graph evaluation
- `capassigner.core.metrics.Solution` - Result wrapping
- `capassigner.ui.plots` - Circuit visualization
- `pytest` - Testing framework

---

## Open Questions

1. **Capacitor Reuse Default**: Should `allow_capacitor_reuse` default to True or False?
   - **Recommendation**: True (classroom example requires it)

2. **Progress Granularity**: How often to fire progress callbacks?
   - **Recommendation**: Every 100 topologies or every 0.5 seconds

3. **Internal Node Naming**: Should internal nodes always be C, D, E, or allow custom names?
   - **Recommendation**: Fixed C, D, E for simplicity

4. **Visualization**: How to display topologies with internal nodes in UI?
   - **Recommendation**: NetworkX spring layout + matplotlib for now, improve later

5. **Graceful Degradation**: If time limit hit, return partial results or error?
   - **Recommendation**: Return partial results with warning

---

## Acceptance Criteria

This feature is considered **complete** when:

1. ✅ Classroom example (N=4, k=2) finds C_eq=1.0pF with error <1e-10
2. ✅ Algorithm generates correct topology count for N=3, k=1 (manual verification)
3. ✅ Performance meets targets (N=4, k=2 in <2 minutes)
4. ✅ UI integration complete with warnings and progress
5. ✅ All tests passing (unit, integration, regression)
6. ✅ Documentation complete (docstrings, theory, README)
7. ✅ Code reviewed and approved
8. ✅ Benchmarks published

---

**Next Steps**: Begin Phase 1 implementation with T001-T007. Estimated start date: After 003-unit-test-suite completion.


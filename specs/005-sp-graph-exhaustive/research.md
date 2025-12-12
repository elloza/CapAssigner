# Research: SP Graph Exhaustive Algorithm

**Feature**: SP Graph Exhaustive Method  
**Date**: December 12, 2025  
**Status**: Complete

## 1. Problem Analysis

The current "SP Tree" method generates binary trees, which corresponds to series-parallel graphs that can be constructed by recursively joining two subgraphs in series or parallel. However, this representation misses topologies that have "internal nodes" in their initial representation but are still SP-reducible.

**Example**: The "Classroom Problem"
- Topology: A-C1-C-C2-D-C3-B with C4 connected between C and D.
- This graph has internal nodes C and D.
- It is SP-reducible: C2 and C4 are in parallel between C and D (if C2 is C-D and C4 is C-D).
- Wait, the classroom example description was: `A ---C1--- C ---C2--- D ---C3--- B` with `C4` in parallel with `C2`.
- Actually, if C4 is in parallel with C2, then they share nodes C and D.
- In a binary tree representation `Series(C1, Series(Parallel(C2, C4), C3))` works.
- **Correction**: The user said the classroom example *failed* with SP Tree. This implies the structure is NOT just simple series/parallel of components, or the SP Tree enumeration missed it.
- **Re-evaluation**: If `C2` and `C4` are in parallel, they share nodes C and D. The structure is `A-C1-C-(C2||C4)-D-C3-B`. This IS a tree: `Series(C1, Series(Parallel(C2, C4), C3))`.
- **Why did SP Tree fail?**
  - Maybe the SP Tree enumeration logic is incomplete?
  - OR the user's description of the circuit is more complex, e.g., a bridge that *becomes* SP reducible?
  - The user said: "The circuit IS SP-reducible but needs graph-based SP reduction, not tree-based".
  - This implies the graph structure allows operations (like node identification) that the tree builder doesn't.
  - **Hypothesis**: The graph generation approach is more robust because it covers *all* connected topologies, then checks reducibility. The Tree approach constructs from bottom-up and might miss specific permutations or structures that don't fit the strict binary build-up (though theoretically SP graphs = SP trees).
  - **Regardless**, the user wants the Graph-based approach.

## 2. Algorithm Selection

### A. Graph Generation (Topology Enumeration)
We need to enumerate all connected multigraphs with $E$ edges and 2 terminals.

**Algorithm**:
1. Iterate number of nodes $V$ from 2 to $E+1$.
2. Generate all combinations of $E$ edges on $V$ nodes (multigraph allowed).
3. Filter for connectivity.
4. Filter for isomorphism (using NetworkX `is_isomorphic`).
5. For each unique graph, iterate all pairs $(A, B)$ as terminals.
6. Filter for terminal-isomorphism.

**Complexity**:
- For $E=4$, $V \in [2, 5]$. Number of graphs is small (< 100).
- For $E=6$, it grows but is manageable for "Exhaustive" search (< 30s).

### B. Capacitor Assignment
Assign input capacitors to the edges of the generated graphs.

**Algorithm**:
1. Generate all unique permutations of input capacitors.
2. Assign to edges.
3. Optimization: If graph has parallel edges, order doesn't matter for those edges (can prune).

### C. Iterative SP Reduction
Calculate $C_{eq}$ by iteratively reducing the graph.

**Algorithm**:
1. **Parallel Reduction**: Identify edges $(u, v)$ with multiplicity $> 1$. Sum capacitances. Replace with single edge.
2. **Series Reduction**: Identify node $n$ (not $A, B$) with degree 2. Neighbors $u, v$. Calculate $C_s = (1/C_{u,n} + 1/C_{n,v})^{-1}$. Remove $n$, add edge $(u, v)$.
3. **Repeat** until no changes.
4. **Result**: If graph is single edge $A-B$, return value. Else, not SP-reducible.

## 3. Implementation Strategy

**Module**: `capassigner/core/sp_graph_exhaustive.py`

**Key Functions**:
- `generate_topologies(num_edges: int) -> List[nx.MultiGraph]`
- `solve_sp_graph(capacitors: List[float], target: float) -> List[Solution]`
- `is_sp_reducible(graph: nx.MultiGraph, term_a, term_b) -> Optional[float]`

**Dependencies**:
- `networkx` for graph operations and isomorphism checks.
- `itertools` for combinations/permutations.

## 4. Alternatives Considered

- **Fixing SP Tree**: Might be harder to debug why it missed the case. Graph approach is more "brute force" and guaranteed to find it if it exists as a graph.
- **Heuristic only**: User wants *exact* solution for small N, not just heuristic.

## 5. Decision

Implement **SP Graph Exhaustive** using NetworkX for topology generation and iterative reduction. This guarantees finding the "Classroom Solution" if it exists as a graph, satisfying the user's core requirement.

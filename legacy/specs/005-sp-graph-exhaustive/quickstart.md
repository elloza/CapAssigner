# Quickstart: SP Graph Exhaustive

**Feature**: SP Graph Exhaustive Method  
**Date**: December 12, 2025

## Overview

The SP Graph Exhaustive method enumerates all possible connected multigraph topologies for a given set of capacitors and determines if they are Series-Parallel (SP) reducible. This allows finding solutions that have internal nodes (bridge-like structures) which are still SP-reducible, covering cases that the tree-based SP method misses.

## Usage

### 1. Running the Solver

```python
from capassigner.core.sp_graph_exhaustive import solve

capacitors = [3e-12, 2e-12, 3e-12, 1e-12]
target = 1e-12

solutions = solve(capacitors, target)

for sol in solutions:
    print(f"C_eq: {sol.ceq}, Error: {sol.absolute_error}")
    print(f"Topology: {sol.expression}")
```

### 2. Checking Reducibility

```python
import networkx as nx
from capassigner.core.sp_graph_exhaustive import is_sp_reducible

G = nx.MultiGraph()
G.add_edge('A', 'C', capacity=3e-12)
G.add_edge('C', 'D', capacity=2e-12)
# ... add other edges ...

ceq = is_sp_reducible(G, 'A', 'B')
if ceq:
    print(f"Reducible! C_eq = {ceq}")
else:
    print("Not SP reducible")
```

## Key Concepts

- **Topology Enumeration**: We generate all connected multigraphs with $E$ edges on $V \in [2, E+1]$ nodes.
- **Iterative Reduction**:
  - **Parallel**: Merge edges between same nodes ($C = C_1 + C_2$).
  - **Series**: Remove degree-2 nodes ($C = (1/C_1 + 1/C_2)^{-1}$).
- **Performance**: Feasible for $N \le 6$. For $N > 6$, use Heuristic Search.

## Testing

Run the specific tests for this feature:

```bash
pytest tests/unit/test_sp_graph_exhaustive.py
```

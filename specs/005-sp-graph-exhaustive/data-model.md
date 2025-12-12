# Data Model: SP Graph Exhaustive

**Feature**: SP Graph Exhaustive Method  
**Date**: December 12, 2025  
**Status**: Draft

## 1. Core Entities

### `SPGraphTopology` (extends/uses `GraphTopology`)

We will reuse the existing `GraphTopology` class but ensure it supports `nx.MultiGraph`.

```python
@dataclass
class GraphTopology:
    graph: Union[nx.Graph, nx.MultiGraph]  # Updated to support MultiGraph
    terminal_a: Any
    terminal_b: Any
    internal_nodes: List[Any]
```

### `SPReductionStep` (Internal)

Used to track the reduction steps for documentation/visualization (optional but good for debugging).

```python
@dataclass
class SPReductionStep:
    type: str  # "series" or "parallel"
    nodes: List[Any]  # Nodes involved
    old_edges: List[Any]  # Edges removed
    new_edge: Any  # Edge added
    value: float  # New capacitance
```

## 2. API Contracts

### `capassigner.core.sp_graph_exhaustive`

```python
def solve(
    capacitors: List[float],
    target: float,
    max_results: int = 10,
    progress_callback: Optional[ProgressCallback] = None
) -> List[Solution]:
    """
    Enumerates all connected multigraph topologies for len(capacitors) edges.
    Assigns capacitors to edges.
    Checks SP-reducibility.
    Returns sorted list of Solutions.
    """
    pass

def generate_topologies(num_edges: int) -> List[nx.MultiGraph]:
    """
    Generates all unique connected multigraphs with num_edges.
    """
    pass

def is_sp_reducible(graph: nx.MultiGraph, term_a, term_b) -> Optional[float]:
    """
    Returns C_eq if reducible, else None.
    """
    pass
```

## 3. File Structure Changes

- `capassigner/core/sp_graph_exhaustive.py`: New file.
- `capassigner/core/graphs.py`: Update `GraphTopology` type hint if needed.
- `capassigner/ui/pages.py`: Update to import and use `sp_graph_exhaustive`.

## 4. Database Schema
N/A (No database)

# Data Model: Complete CapAssigner Application

**Feature**: 002-full-app-implementation
**Date**: 2025-10-20
**Status**: Complete

## Overview

This document defines the core data entities, their fields, validation rules, relationships, and state transitions for the CapAssigner application. All entities are designed to support the functional requirements (FR-001 to FR-049) and align with Constitutional Principle IV (Modular Architecture).

---

## Entity Definitions

### 1. Capacitor

**Description**: Individual capacitor component with a capacitance value, part of user's available inventory.

**Fields**:
- `index: int` - Unique identifier within inventory (0-based)
- `value: float` - Capacitance in Farads (stored internally in base SI unit)
- `label: str` - Human-readable label (e.g., "C1", "C2")

**Validation Rules**:
- `value > 0` (must be positive)
- `1e-15 <= value <= 1.0` (typical range: 1fF to 1F; warn if outside)
- `label` must be unique within inventory

**Example**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Capacitor:
    index: int
    value: float  # Farads
    label: str

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(f"Capacitance must be positive, got {self.value}")
        if not (1e-15 <= self.value <= 1.0):
            import warnings
            warnings.warn(f"Capacitance {self.value} F is outside typical range [1fF, 1F]")
```

**Relationships**:
- **Inventory** contains 0 to N capacitors
- **Topology** references capacitors by index
- **Solution** includes capacitors used in the topology

---

### 2. Topology

**Description**: Network structure describing how capacitors are connected. Two representations: SPNode (series-parallel trees) and GraphTopology (general graphs).

#### 2a. SPNode (Series-Parallel Tree)

**Description**: Recursive data structure for series-parallel topologies.

**Variants**:
1. **Leaf**: Single capacitor
2. **Series**: Two sub-topologies connected in series
3. **Parallel**: Two sub-topologies connected in parallel

**Fields** (discriminated union using Python dataclasses or enum):
```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Leaf:
    capacitor_index: int
    value: float  # Cached for performance

@dataclass(frozen=True)
class Series:
    left: 'SPNode'
    right: 'SPNode'

@dataclass(frozen=True)
class Parallel:
    left: 'SPNode'
    right: 'SPNode'

SPNode = Union[Leaf, Series, Parallel]
```

**Validation Rules**:
- Leaf: `capacitor_index` must be valid (exists in inventory)
- Series/Parallel: `left` and `right` must be non-None SPNodes
- No cycles (enforced by tree structure)

**Operations**:
- `calculate_ceq(node: SPNode) -> float`: Recursively compute equivalent capacitance
  - Leaf: return `node.value`
  - Series: return `1 / (1/ceq_left + 1/ceq_right)`
  - Parallel: return `ceq_left + ceq_right`
- `to_expression(node: SPNode) -> str`: Generate topology string (e.g., "((C1||C2)+C3)")
  - Leaf: return capacitor label
  - Series: return `f"({left_expr}+{right_expr})"`
  - Parallel: return `f"({left_expr}||{right_expr})"`

**Example**:
```python
# Topology: (C1 || C2) + C3
topology = Series(
    left=Parallel(
        left=Leaf(0, 5.2e-12),
        right=Leaf(1, 10e-12)
    ),
    right=Leaf(2, 3.3e-12)
)
# C_eq = 1 / (1/(5.2e-12 + 10e-12) + 1/3.3e-12) ≈ 2.89pF
```

---

#### 2b. GraphTopology (General Graph)

**Description**: General network with nodes and edges (capacitors).

**Fields**:
- `graph: nx.Graph` - NetworkX graph object
- `terminal_a: str` - Node identifier for terminal A (e.g., "A")
- `terminal_b: str` - Node identifier for terminal B (e.g., "B")
- `internal_nodes: list[str]` - Additional internal nodes (e.g., ["n1", "n2"])

**Edge Attributes**:
- `capacitance: float` - Capacitance value in Farads for each edge

**Validation Rules**:
- `graph` must contain `terminal_a` and `terminal_b` as nodes
- All edges must have `capacitance` attribute (positive float)
- Graph should be connected (warn if not; C_eq=0 for disconnected)
- No self-loops (capacitor cannot connect node to itself)

**Operations**:
- `calculate_ceq_laplacian(graph: nx.Graph, terminal_a: str, terminal_b: str) -> float`: Use Laplacian matrix method (see research.md)
- `is_connected(graph: nx.Graph, terminal_a: str, terminal_b: str) -> bool`: Check if path exists between A and B
- `visualize(graph: nx.Graph) -> matplotlib.Figure`: Render graph with NetworkX layout

**Example**:
```python
import networkx as nx

# Bridge network
G = nx.Graph()
G.add_edge('A', 'n1', capacitance=5e-12)
G.add_edge('A', 'n2', capacitance=10e-12)
G.add_edge('n1', 'B', capacitance=3.3e-12)
G.add_edge('n2', 'B', capacitance=2.2e-12)
G.add_edge('n1', 'n2', capacitance=1e-12)  # Bridge capacitor

topology = GraphTopology(
    graph=G,
    terminal_a='A',
    terminal_b='B',
    internal_nodes=['n1', 'n2']
)
```

---

### 3. Solution

**Description**: A topology with its calculated equivalent capacitance and error metrics.

**Fields**:
- `topology: Union[SPNode, GraphTopology]` - Network structure
- `ceq: float` - Equivalent capacitance in Farads
- `target: float` - Target capacitance in Farads (for error calculation)
- `absolute_error: float` - |C_eq - C_target| in Farads
- `relative_error: float` - (|C_eq - C_target| / C_target) × 100 (percentage)
- `within_tolerance: bool` - True if relative_error <= tolerance threshold
- `expression: str` - Human-readable topology description (e.g., "((C1||C2)+C3)" or "Bridge network")
- `diagram: Optional[matplotlib.Figure]` - Visual representation (SchemDraw or NetworkX)

**Validation Rules**:
- `ceq >= 0` (can be zero for disconnected networks)
- `target > 0` (target must be positive; checked during parsing)
- `absolute_error = abs(ceq - target)`
- `relative_error = (absolute_error / target) * 100` if `target > 0`, else `float('inf')`

**Example**:
```python
from dataclasses import dataclass
from typing import Union, Optional
import matplotlib.pyplot as plt

@dataclass
class Solution:
    topology: Union[SPNode, GraphTopology]
    ceq: float
    target: float
    absolute_error: float
    relative_error: float
    within_tolerance: bool
    expression: str
    diagram: Optional[plt.Figure] = None

    @staticmethod
    def from_topology(
        topology: Union[SPNode, GraphTopology],
        target: float,
        tolerance: float
    ) -> 'Solution':
        ceq = calculate_ceq(topology)
        abs_err = abs(ceq - target)
        rel_err = (abs_err / target) * 100 if target > 0 else float('inf')
        within_tol = rel_err <= tolerance
        expr = topology_to_expression(topology)
        return Solution(
            topology=topology,
            ceq=ceq,
            target=target,
            absolute_error=abs_err,
            relative_error=rel_err,
            within_tolerance=within_tol,
            expression=expr,
            diagram=None  # Generated separately for performance
        )
```

**Relationships**:
- **Solution** contains a **Topology** (either SPNode or GraphTopology)
- Multiple **Solutions** are ranked by error for a given target

---

### 4. SearchParameters

**Description**: Configuration for search algorithms (SP exhaustive or heuristic graph search).

**Fields**:
- `method: Literal["sp_exhaustive", "heuristic_graph"]` - Algorithm selection
- `tolerance: float` - Acceptable relative error percentage (default 5.0 for ±5%)
- `sp_max_n: int` - Maximum N for SP exhaustive (default 8, from config.py)
- `heuristic_iters: int` - Number of random graphs to generate (default 2000)
- `heuristic_max_internal: int` - Max internal nodes in heuristic graphs (default 2)
- `heuristic_seed: int` - Random seed for determinism (default 0)

**Validation Rules**:
- `tolerance >= 0` (percentage; 0 means exact match only)
- `sp_max_n >= 1` (need at least 1 capacitor)
- `heuristic_iters >= 1` (need at least 1 iteration)
- `heuristic_max_internal >= 0` (0 means only A and B, no internal nodes)
- `heuristic_seed >= 0` (non-negative integer for reproducibility)

**Example**:
```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class SearchParameters:
    method: Literal["sp_exhaustive", "heuristic_graph"]
    tolerance: float = 5.0  # ±5%
    sp_max_n: int = 8
    heuristic_iters: int = 2000
    heuristic_max_internal: int = 2
    heuristic_seed: int = 0
```

**Relationships**:
- **SearchParameters** are inputs to search functions
- Stored in session state for UI persistence

---

### 5. ProgressUpdate

**Description**: Progress information for long-running computations.

**Fields**:
- `current: int` - Current iteration or topology count
- `total: int` - Total iterations or topologies to process
- `message: str` - Descriptive text (e.g., "Exploring topology 123/1000")
- `best_error: Optional[float]` - Best error found so far (for heuristic search)

**Example**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProgressUpdate:
    current: int
    total: int
    message: str
    best_error: Optional[float] = None
```

**Usage**:
```python
from typing import Callable

ProgressCallback = Callable[[ProgressUpdate], None]

def search_topologies(
    capacitors: list[Capacitor],
    params: SearchParameters,
    progress_cb: Optional[ProgressCallback] = None
) -> list[Solution]:
    for i in range(params.heuristic_iters):
        # ... compute topology ...
        if progress_cb and i % 50 == 0:
            progress_cb(ProgressUpdate(
                current=i,
                total=params.heuristic_iters,
                message=f"Iteration {i}/{params.heuristic_iters}",
                best_error=current_best_error
            ))
    return solutions
```

---

### 6. ParsedCapacitance

**Description**: Result of parsing capacitance input string.

**Fields**:
- `success: bool` - True if parsing succeeded
- `value: Optional[float]` - Parsed value in Farads (None if failed)
- `error_message: Optional[str]` - Error explanation (None if succeeded)
- `formatted: str` - Human-readable format (e.g., "5.2pF")

**Example**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedCapacitance:
    success: bool
    value: Optional[float]
    error_message: Optional[str]
    formatted: str

# Success case
parse_capacitance("5.2pF")
# -> ParsedCapacitance(success=True, value=5.2e-12, error_message=None, formatted="5.2pF")

# Error case
parse_capacitance("5pf")
# -> ParsedCapacitance(success=False, value=None, error_message="Invalid format '5pf' — use '5pF' with capital F", formatted="")
```

**Validation Rules**:
- If `success=True`, `value` must be non-None and `error_message` must be None
- If `success=False`, `value` must be None and `error_message` must be non-None

---

## Entity Relationships

```
┌─────────────────┐
│   Inventory     │ (list of Capacitors)
│  (Session State)│
└────────┬────────┘
         │ contains
         ↓
    ┌─────────────┐
    │  Capacitor  │ (individual component)
    └─────────────┘
         │ referenced by
         ↓
    ┌─────────────┐
    │  Topology   │ (SPNode or GraphTopology)
    └─────────────┘
         │ included in
         ↓
    ┌─────────────┐
    │  Solution   │ (topology + metrics)
    └─────────────┘
         │ ranked in
         ↓
    ┌─────────────┐
    │ SolutionList│ (search results)
    └─────────────┘

┌──────────────────┐
│ SearchParameters │ (configuration)
└──────────────────┘
         │ used by
         ↓
    ┌─────────────────┐
    │ Search Function │ (sp_exhaustive or heuristic)
    └─────────────────┘
         │ produces
         ↓
    ┌─────────────┐
    │ SolutionList│
    └─────────────┘

┌──────────────────┐
│ ProgressCallback │ (optional)
└──────────────────┘
         │ receives
         ↓
    ┌──────────────┐
    │ ProgressUpdate│
    └──────────────┘
```

---

## State Transitions

### Application State (Session State)

The application maintains the following state throughout a user session:

**Initial State** (on app start):
- `inventory: list[Capacitor]` = [] (empty)
- `target_capacitance: Optional[float]` = None
- `search_params: SearchParameters` = default values
- `solutions: list[Solution]` = []
- `current_page: str` = "main"

**State Transitions**:

1. **User adds/removes capacitors**:
   - `inventory` is updated
   - `solutions` is cleared (invalidated)

2. **User enters target capacitance**:
   - `target_capacitance` is parsed and validated
   - If invalid, show error and keep previous value
   - If valid, update `target_capacitance`

3. **User changes search parameters**:
   - `search_params` is updated
   - `solutions` is cleared (invalidated)

4. **User clicks "Find Solutions"**:
   - Validate inputs (target, inventory, params)
   - If invalid, show errors and stay in current state
   - If valid, execute search:
     - Show progress bar
     - Generate solutions
     - Update `solutions` with results
     - Hide progress bar

5. **User filters results** (e.g., "Show only within tolerance"):
   - Display filtered view of `solutions`
   - Do not modify underlying `solutions` list

**State Persistence**:
- All state is stored in `st.session_state` (Streamlit)
- State persists across widget interactions within a session
- State is lost when browser tab is closed (no cross-session persistence for MVP)

---

### Solution State

Each solution has a lifecycle:

1. **Generated**: Topology created and C_eq calculated
2. **Ranked**: Sorted by error among all solutions
3. **Displayed**: Shown in results table
4. **Visualized**: Diagram generated on demand (lazy loading for performance)

**Diagram Generation** (lazy loading):
- Solutions initially have `diagram=None`
- When user expands a solution row, diagram is generated
- Diagram is cached in session state to avoid recomputation

---

## Data Validation Summary

| Entity | Key Validations |
|--------|----------------|
| Capacitor | value > 0, within typical range [1fF, 1F] |
| SPNode | capacitor_index valid, no cycles (enforced by tree structure) |
| GraphTopology | terminals exist, all edges have capacitance, warn if disconnected |
| Solution | ceq >= 0, target > 0, errors calculated correctly |
| SearchParameters | tolerance >= 0, sp_max_n >= 1, heuristic_iters >= 1, seed >= 0 |
| ParsedCapacitance | success implies value is non-None, failure implies error_message is non-None |
| ProgressUpdate | 0 <= current <= total |

---

## Type Definitions (for implementation)

```python
# capassigner/core/sp_structures.py
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Leaf:
    capacitor_index: int
    value: float

@dataclass(frozen=True)
class Series:
    left: 'SPNode'
    right: 'SPNode'

@dataclass(frozen=True)
class Parallel:
    left: 'SPNode'
    right: 'SPNode'

SPNode = Union[Leaf, Series, Parallel]

# capassigner/core/graphs.py
import networkx as nx

@dataclass
class GraphTopology:
    graph: nx.Graph
    terminal_a: str
    terminal_b: str
    internal_nodes: list[str]

# capassigner/core/metrics.py
from dataclasses import dataclass
from typing import Union, Optional
import matplotlib.pyplot as plt

@dataclass
class Solution:
    topology: Union[SPNode, GraphTopology]
    ceq: float
    target: float
    absolute_error: float
    relative_error: float
    within_tolerance: bool
    expression: str
    diagram: Optional[plt.Figure] = None

# capassigner/core/parsing.py
@dataclass
class ParsedCapacitance:
    success: bool
    value: Optional[float]
    error_message: Optional[str]
    formatted: str
```

---

## Invariants

The following invariants must hold at all times:

1. **Capacitor values are positive**: No capacitor in inventory has value <= 0
2. **Target is positive**: When set, target_capacitance > 0
3. **Solutions are sorted**: Solution list is always sorted by absolute_error (ascending)
4. **Error consistency**: For each solution, `absolute_error = |ceq - target|` and `relative_error = (absolute_error / target) * 100`
5. **Topology validity**: All SPNodes reference valid capacitor indices; all GraphTopologies have A and B terminals
6. **Modular separation**: core/ modules never import streamlit; ui/ modules never directly implement circuit calculations

---

**Data Model Complete**: 2025-10-20

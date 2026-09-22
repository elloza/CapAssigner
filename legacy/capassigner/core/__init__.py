"""Core computational modules for CapAssigner.

This package contains pure computational logic with NO Streamlit dependencies.
All modules follow Constitutional Principle IV: Modular Architecture.

Modules:
    - parsing: Input parsing and validation
    - sp_structures: Series-Parallel tree data structures
    - sp_enumeration: Enumeration algorithms for SP networks
    - graphs: General graph-based capacitor network algorithms
    - heuristics: Heuristic search algorithms for graph networks
    - metrics: Solution quality metrics and ranking

Design Principles:
    - All functions accept progress_cb: Callable[[int, int], None] | None = None
    - All functions use modern type hints (PEP 484, PEP 585, PEP 604)
    - All public functions have Google-style docstrings
    - NO Streamlit imports allowed in this package
"""

from capassigner.core import (
    graphs,
    heuristics,
    metrics,
    parsing,
    sp_enumeration,
    sp_structures,
)

# Export key types for easy access
from capassigner.core.sp_structures import (
    Capacitor,
    Leaf,
    Series,
    Parallel,
    SPNode,
)
from capassigner.core.metrics import (
    ProgressUpdate,
    ProgressCallback,
    Solution,
)
from capassigner.core.graphs import (
    GraphTopology,
    build_laplacian_matrix,
    is_connected_between_terminals,
    calculate_graph_ceq,
)
from capassigner.core.heuristics import (
    generate_random_graph,
    heuristic_search,
)

__all__ = [
    # Modules
    "graphs",
    "heuristics",
    "metrics",
    "parsing",
    "sp_enumeration",
    "sp_structures",
    # SP Types
    "Capacitor",
    "Leaf",
    "Series",
    "Parallel",
    "SPNode",
    # Metrics Types
    "ProgressUpdate",
    "ProgressCallback",
    "Solution",
    # Graph Types
    "GraphTopology",
    "build_laplacian_matrix",
    "is_connected_between_terminals",
    "calculate_graph_ceq",
    # Heuristics
    "generate_random_graph",
    "heuristic_search",
]

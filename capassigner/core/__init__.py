"""Core computational modules for CapAssigner.

This package contains pure computational logic with NO Streamlit dependencies.
All modules follow Constitutional Principle IV: Modular Architecture.

Modules:
    - parsing: Input parsing and validation
    - sp_structures: Series-Parallel tree data structures
    - sp_enumeration: Enumeration algorithms for SP networks
    - graphs: General graph-based capacitor network algorithms
    - heuristics: Metaheuristic optimization algorithms (GA, SA, PSO)
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

__all__ = [
    "graphs",
    "heuristics",
    "metrics",
    "parsing",
    "sp_enumeration",
    "sp_structures",
]

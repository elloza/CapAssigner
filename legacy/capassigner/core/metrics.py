"""Error calculation and tolerance checking.

This module provides functions for calculating absolute and relative errors,
checking tolerance compliance, and ranking solutions by error metrics.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Exact error formulas
    - Principle IV (Modular Architecture): No Streamlit imports
"""

from __future__ import annotations
from typing import Any, Callable, List, Union, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from capassigner.core.sp_structures import SPNode
    from capassigner.core.graphs import GraphTopology


@dataclass
class ProgressUpdate:
    """Progress information for long-running computations.

    Attributes:
        current: Current iteration or topology count.
        total: Total iterations or topologies to process.
        message: Descriptive text (e.g., "Exploring topology 123/1000").
        best_error: Best error found so far (for heuristic search; None for SP).
    """
    current: int
    total: int
    message: str
    best_error: Optional[float] = None


# Type alias for progress callback function
ProgressCallback = Callable[[ProgressUpdate], None]


@dataclass
class Solution:
    """Complete solution with topology and error metrics.

    Attributes:
        topology: Network structure (SPNode or GraphTopology).
        ceq: Equivalent capacitance in Farads.
        target: Target capacitance in Farads.
        absolute_error: |C_eq - C_target| in Farads.
        relative_error: (|C_eq - C_target| / C_target) × 100 (percentage).
        within_tolerance: True if relative_error <= tolerance.
        expression: Human-readable topology (e.g., "((C1||C2)+C3)").
        diagram: Visual representation (generated lazily, initially None).
    """
    topology: Any  # Union[SPNode, GraphTopology] but avoiding circular import
    ceq: float
    target: float
    absolute_error: float
    relative_error: float
    within_tolerance: bool
    expression: str
    diagram: Optional[Any] = None  # matplotlib.Figure

    def is_graph_topology(self) -> bool:
        """Check if this solution uses a graph topology (not SP).

        Returns:
            True if topology is a GraphTopology, False if SPNode.
        """
        # Import here to avoid circular import
        from capassigner.core.graphs import GraphTopology
        return isinstance(self.topology, GraphTopology)


def calculate_absolute_error(ceq: float, target: float) -> float:
    """Calculate absolute error between equivalent and target capacitance.

    Formula: error_abs = |C_eq - C_target|

    Args:
        ceq: Equivalent capacitance in Farads.
        target: Target capacitance in Farads.

    Returns:
        Absolute error in Farads (always non-negative).

    Examples:
        >>> calculate_absolute_error(5.2e-12, 5.0e-12)
        2e-13
        >>> calculate_absolute_error(3.0e-12, 5.0e-12)
        2e-12
    """
    return abs(ceq - target)


def calculate_relative_error(ceq: float, target: float) -> float:
    """Calculate relative error as percentage.

    Formula: error_rel = (|C_eq - C_target| / C_target) × 100

    Args:
        ceq: Equivalent capacitance in Farads.
        target: Target capacitance in Farads (must be > 0).

    Returns:
        Relative error as percentage (always non-negative).

    Raises:
        ValueError: If target is zero (division by zero).

    Examples:
        >>> calculate_relative_error(5.2e-12, 5.0e-12)
        4.0  # 4% error
        >>> calculate_relative_error(3.0e-12, 5.0e-12)
        40.0  # 40% error
    """
    if target == 0:
        raise ValueError("Cannot calculate relative error with zero target")
    return (abs(ceq - target) / target) * 100.0


def check_within_tolerance(relative_error: float, tolerance: float) -> bool:
    """Check if solution is within tolerance threshold.

    Args:
        relative_error: Relative error percentage.
        tolerance: Tolerance threshold percentage (e.g., 5.0 for ±5%).

    Returns:
        True if relative_error <= tolerance, False otherwise.

    Examples:
        >>> check_within_tolerance(3.0, 5.0)
        True  # 3% is within ±5%
        >>> check_within_tolerance(7.0, 5.0)
        False  # 7% exceeds ±5%
    """
    return relative_error <= tolerance


def create_solution(
    topology: Any,
    ceq: float,
    target: float,
    tolerance: float,
    expression: str
) -> Solution:
    """Create Solution object with all metrics calculated.

    Args:
        topology: Network topology (SPNode or GraphTopology).
        ceq: Equivalent capacitance in Farads.
        target: Target capacitance in Farads (must be > 0).
        tolerance: Tolerance threshold percentage.
        expression: Human-readable topology string.

    Returns:
        Complete Solution with all fields populated.

    Raises:
        ValueError: If target <= 0.
    """
    if target <= 0:
        raise ValueError("Target capacitance must be positive")

    abs_err = calculate_absolute_error(ceq, target)
    rel_err = calculate_relative_error(ceq, target)
    within_tol = check_within_tolerance(rel_err, tolerance)

    return Solution(
        topology=topology,
        ceq=ceq,
        target=target,
        absolute_error=abs_err,
        relative_error=rel_err,
        within_tolerance=within_tol,
        expression=expression,
        diagram=None  # Generated lazily in UI
    )


def rank_solutions(solutions: List[Solution]) -> List[Solution]:
    """Sort solutions by absolute error (best first).

    Args:
        solutions: Unsorted list of solutions.

    Returns:
        Solutions sorted by absolute_error ascending (smallest error first).

    Examples:
        >>> s1 = Solution(..., absolute_error=2.0, ...)
        >>> s2 = Solution(..., absolute_error=0.5, ...)
        >>> s3 = Solution(..., absolute_error=1.0, ...)
        >>> ranked = rank_solutions([s1, s2, s3])
        >>> [s.absolute_error for s in ranked]
        [0.5, 1.0, 2.0]
    """
    return sorted(solutions, key=lambda s: s.absolute_error)


def filter_by_tolerance(solutions: List[Solution]) -> List[Solution]:
    """Filter solutions to only those within tolerance.

    Args:
        solutions: List of solutions (may include out-of-tolerance).

    Returns:
        Only solutions where within_tolerance == True.
        Preserves order (does not re-sort).
        Returns empty list if no solutions meet tolerance.
    """
    return [s for s in solutions if s.within_tolerance]

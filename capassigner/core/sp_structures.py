"""Series-Parallel data structures module.

This module defines data types for representing series-parallel network
topologies, including Capacitor, Leaf (single capacitor), Series, and Parallel structures.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Formulas match exact definitions
    - Principle IV (Modular Architecture): No Streamlit imports
"""

from __future__ import annotations
from typing import Callable, List, Union, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Capacitor:
    """Individual capacitor component.

    Attributes:
        index: Unique identifier within inventory (0-based).
        value: Capacitance in Farads (must be positive).
        label: Human-readable label (e.g., "C1", "C2").
    """
    index: int
    value: float
    label: str

    def __post_init__(self):
        """Validate capacitor values."""
        if self.value <= 0:
            raise ValueError(f"Capacitance must be positive, got {self.value}")


@dataclass(frozen=True)
class Leaf:
    """Leaf node representing a single capacitor in SP tree.

    Attributes:
        capacitor_index: Index into capacitor inventory.
        value: Capacitance value in Farads (cached for performance).
    """
    capacitor_index: int
    value: float


@dataclass(frozen=True)
class Series:
    """Series connection of two SP networks.

    Formula: C_series = 1 / (1/C_left + 1/C_right)

    Attributes:
        left: Left sub-topology.
        right: Right sub-topology.
    """
    left: 'SPNode'
    right: 'SPNode'


@dataclass(frozen=True)
class Parallel:
    """Parallel connection of two SP networks.

    Formula: C_parallel = C_left + C_right

    Attributes:
        left: Left sub-topology.
        right: Right sub-topology.
    """
    left: 'SPNode'
    right: 'SPNode'


# Type alias for Series-Parallel node (Union of variants)
SPNode = Union[Leaf, Series, Parallel]


def calculate_sp_ceq(node: SPNode) -> float:
    """Calculate equivalent capacitance for series-parallel topology.

    This implements the exact formulas from Constitutional Principle I:
    - Leaf: C_eq = value
    - Series: C_eq = 1 / (1/C_left + 1/C_right)
    - Parallel: C_eq = C_left + C_right

    Args:
        node: Root of SP tree (Leaf, Series, or Parallel).

    Returns:
        Equivalent capacitance in Farads.

    Raises:
        ZeroDivisionError: If series connection has zero-value capacitor.
    """
    if isinstance(node, Leaf):
        return node.value
    elif isinstance(node, Series):
        c_left = calculate_sp_ceq(node.left)
        c_right = calculate_sp_ceq(node.right)
        if c_left == 0 or c_right == 0:
            raise ZeroDivisionError(
                "Cannot compute series capacitance with zero-value capacitor"
            )
        return 1.0 / (1.0 / c_left + 1.0 / c_right)
    elif isinstance(node, Parallel):
        c_left = calculate_sp_ceq(node.left)
        c_right = calculate_sp_ceq(node.right)
        return c_left + c_right
    else:
        raise TypeError(f"Unknown SPNode type: {type(node)}")


def sp_node_to_expression(node: SPNode, capacitor_labels: List[str]) -> str:
    """Generate human-readable topology expression from SP tree.

    Notation:
    - "+" for series connection
    - "||" for parallel connection
    - Parentheses for grouping

    Args:
        node: Root of SP tree.
        capacitor_labels: Labels for capacitors (e.g., ["C1", "C2", "C3"]).

    Returns:
        Expression string like "((C1||C2)+C3)".

    Examples:
        >>> leaf = Leaf(0, 5e-12)
        >>> sp_node_to_expression(leaf, ["C1"])
        'C1'
        >>> series = Series(Leaf(0, 5e-12), Leaf(1, 10e-12))
        >>> sp_node_to_expression(series, ["C1", "C2"])
        '(C1+C2)'
        >>> parallel = Parallel(Leaf(0, 5e-12), Leaf(1, 10e-12))
        >>> sp_node_to_expression(parallel, ["C1", "C2"])
        '(C1||C2)'
    """
    if isinstance(node, Leaf):
        return capacitor_labels[node.capacitor_index]
    elif isinstance(node, Series):
        left_expr = sp_node_to_expression(node.left, capacitor_labels)
        right_expr = sp_node_to_expression(node.right, capacitor_labels)
        return f"({left_expr}+{right_expr})"
    elif isinstance(node, Parallel):
        left_expr = sp_node_to_expression(node.left, capacitor_labels)
        right_expr = sp_node_to_expression(node.right, capacitor_labels)
        return f"({left_expr}||{right_expr})"
    else:
        raise TypeError(f"Unknown SPNode type: {type(node)}")

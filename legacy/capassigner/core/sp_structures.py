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


def _collect_operands(node: SPNode, op_type: type, capacitor_labels: List[str]) -> List[str]:
    """Collect all operands of the same operation type (flattening associativity).
    
    For example, for Series(Series(A, B), C), this returns [norm(A), norm(B), norm(C)]
    instead of treating it as two nested series operations.
    
    Args:
        node: Current node to process.
        op_type: The operation type to flatten (Series or Parallel).
        capacitor_labels: Labels for capacitors.
    
    Returns:
        List of normalized expression strings for all operands.
    """
    if isinstance(node, op_type):
        # Recursively collect from both branches
        left_ops = _collect_operands(node.left, op_type, capacitor_labels)
        right_ops = _collect_operands(node.right, op_type, capacitor_labels)
        return left_ops + right_ops
    else:
        # Different operation type or leaf - normalize and return as single operand
        return [sp_node_to_normalized_expression(node, capacitor_labels)]


def sp_node_to_normalized_expression(node: SPNode, capacitor_labels: List[str]) -> str:
    """Generate normalized topology expression for deduplication.

    Normalizes expressions to handle both commutativity and associativity:
    - Commutativity: (C1+C2) == (C2+C1)
    - Associativity: (C1+(C2+C3)) == ((C1+C2)+C3)
    
    The normalization:
    1. Flattens consecutive same-type operations
    2. Sorts all operands alphabetically
    3. Produces a canonical form
    
    Args:
        node: Root of SP tree.
        capacitor_labels: Labels for capacitors (e.g., ["C1", "C2", "C3"]).

    Returns:
        Normalized expression string.

    Examples:
        >>> # Commutativity
        >>> series1 = Series(Leaf(0, 5e-12), Leaf(1, 10e-12))
        >>> series2 = Series(Leaf(1, 10e-12), Leaf(0, 5e-12))
        >>> sp_node_to_normalized_expression(series1, ["C1", "C2"])
        '(C1+C2)'
        >>> sp_node_to_normalized_expression(series2, ["C1", "C2"])
        '(C1+C2)'
        >>> # Associativity: (C1+(C2+C3)) == ((C1+C2)+C3)
    """
    if isinstance(node, Leaf):
        return capacitor_labels[node.capacitor_index]
    elif isinstance(node, Series):
        # Collect all operands, flattening nested series
        operands = _collect_operands(node, Series, capacitor_labels)
        # Sort operands for canonical form
        operands.sort()
        # Join with + operator
        return "(" + "+".join(operands) + ")"
    elif isinstance(node, Parallel):
        # Collect all operands, flattening nested parallels
        operands = _collect_operands(node, Parallel, capacitor_labels)
        # Sort operands for canonical form
        operands.sort()
        # Join with || operator
        return "(" + "||".join(operands) + ")"
    else:
        raise TypeError(f"Unknown SPNode type: {type(node)}")

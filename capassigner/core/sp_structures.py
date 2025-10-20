"""Series-Parallel data structures module.

This module defines data types for representing series-parallel network
topologies, including Leaf (single capacitor), Series, and Parallel structures.

This is a placeholder module created during scaffolding.
Implementation details will be added in subsequent features.
"""

from __future__ import annotations
from typing import Any, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Leaf:
    """Leaf node representing a single capacitor.

    Attributes:
        idx: Index of the capacitor in the component list.
    """
    idx: int


@dataclass(frozen=True)
class Series:
    """Series connection of two SP networks.

    Attributes:
        left: Left SP node.
        right: Right SP node.
    """
    left: SPNode
    right: SPNode


@dataclass(frozen=True)
class Parallel:
    """Parallel connection of two SP networks.

    Attributes:
        top: Top SP node.
        bottom: Bottom SP node.
    """
    top: SPNode
    bottom: SPNode


# Type alias for Series-Parallel node
SPNode = Leaf | Series | Parallel


def sp_value(
    node: SPNode,
    caps: list[float],
    progress_cb: Callable[[int, int], None] | None = None
) -> float:
    """Calculate equivalent capacitance of SP network.

    Args:
        node: Root node of the SP network.
        caps: List of capacitor values.
        progress_cb: Optional callback for progress updates (current, total).

    Returns:
        Equivalent capacitance in Farads.
    """
    # Placeholder implementation
    pass


def sp_str(
    node: SPNode,
    names: list[str],
    progress_cb: Callable[[int, int], None] | None = None
) -> str:
    """Convert SP network to string representation.

    Args:
        node: Root node of the SP network.
        names: List of capacitor names.
        progress_cb: Optional callback for progress updates (current, total).

    Returns:
        String representation of the network topology.
    """
    # Placeholder implementation
    pass

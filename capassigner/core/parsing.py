"""Capacitance value parsing module.

This module handles parsing of capacitance values from various string formats
including unit suffixes (pF, nF, µF, uF, mF, F) and scientific notation
(e.g., '5.2pF', '1e-11', '1.2*10^-12').

This is a placeholder module created during scaffolding.
Implementation details will be added in subsequent features.
"""

from __future__ import annotations
from typing import Any, Callable


def parse_capacitance(
    value: str,
    progress_cb: Callable[[int, int], None] | None = None
) -> float:
    """Parse capacitance value from string with units.

    Supports multiple formats including scientific notation and unit suffixes
    (pF, nF, µF, uF, mF, F). Case-sensitive for units.

    Args:
        value: String representation of capacitance (e.g., "5.2pF", "1e-11").
        progress_cb: Optional callback for progress updates (current, total).

    Returns:
        Capacitance value in Farads (float).

    Raises:
        ValueError: If value format is invalid or ambiguous.

    Examples:
        >>> parse_capacitance("5.2pF")
        5.2e-12
        >>> parse_capacitance("1e-11")
        1e-11
    """
    # Placeholder implementation
    pass


def format_capacitance(
    value: float,
    progress_cb: Callable[[int, int], None] | None = None
) -> str:
    """Format capacitance value to human-readable string.

    Args:
        value: Capacitance value in Farads.
        progress_cb: Optional callback for progress updates (current, total).

    Returns:
        Formatted string with appropriate unit (e.g., "5.2pF", "1.5nF").
    """
    # Placeholder implementation
    pass

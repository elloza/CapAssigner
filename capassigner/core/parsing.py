"""Capacitance value parsing and formatting module.

This module handles parsing of capacitance values from various string formats
including unit suffixes (pF, nF, µF, uF, mF, F) and scientific notation
(e.g., '5.2pF', '1e-11', '1.2*10^-12').

Constitutional Compliance:
    - Principle III (Robust Input): Comprehensive format support with clear errors
    - Principle IV (Modular Architecture): Pure parsing logic, no UI dependencies
"""

from __future__ import annotations
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class ParsedCapacitance:
    """Result of capacitance parsing operation.

    Attributes:
        success: True if parsing succeeded, False otherwise.
        value: Parsed value in Farads (None if parsing failed).
        error_message: Human-readable error message (None if parsing succeeded).
        formatted: Human-readable formatted string (e.g., "5.2pF").
    """
    success: bool
    value: Optional[float]
    error_message: Optional[str]
    formatted: str


def parse_capacitance(value_str: str) -> ParsedCapacitance:
    """Parse capacitance value from string with comprehensive format support.

    Supports multiple formats:
    - Unit suffixes: 5.2pF, 1nF, 2.7µF, 2.7uF, 1mF, 0.5F
    - Scientific notation: 1e-11, 1.2e-12
    - Engineering notation: 1*10^-11, 1.2*10^-12
    - Plain decimals: 0.0000000001, 5.2 (assumed Farads)

    Validation:
    - Rejects negative values
    - Rejects zero values
    - Rejects lowercase 'f' (must be capital 'F')
    - Case-sensitive for all units

    Args:
        value_str: String representation of capacitance.

    Returns:
        ParsedCapacitance with success status, value, and formatted string.

    Examples:
        >>> result = parse_capacitance("5.2pF")
        >>> result.success
        True
        >>> result.value
        5.2e-12
        >>> result.formatted
        '5.2pF'

        >>> result = parse_capacitance("-5pF")
        >>> result.success
        False
        >>> result.error_message
        'Capacitance must be positive'

        >>> result = parse_capacitance("5pf")
        >>> result.success
        False
        >>> "capital F" in result.error_message
        True
    """
    value_str = value_str.strip()

    # Check for lowercase 'f' (common mistake - T044)
    if value_str.endswith('pf') or value_str.endswith('nf') or value_str.endswith('f'):
        if not value_str.endswith('F'):  # Ensure it's not µF, mF, etc.
            return ParsedCapacitance(
                success=False,
                value=None,
                error_message=f"Invalid format '{value_str}' — use capital F (e.g., '{value_str[:-1]}F')",
                formatted=""
            )

    # Try parsing with different methods
    value = None

    # 1. Try unit suffix parsing (T039)
    value = _parse_with_unit_suffix(value_str)
    if value is not None:
        # Validate (T043)
        if value <= 0:
            return ParsedCapacitance(
                success=False,
                value=None,
                error_message="Capacitance must be positive",
                formatted=""
            )
        formatted = format_capacitance(value)
        return ParsedCapacitance(
            success=True,
            value=value,
            error_message=None,
            formatted=formatted
        )

    # 2. Try scientific/engineering notation (T040)
    value = _parse_scientific_notation(value_str)
    if value is not None:
        if value <= 0:
            return ParsedCapacitance(
                success=False,
                value=None,
                error_message="Capacitance must be positive",
                formatted=""
            )
        formatted = format_capacitance(value)
        return ParsedCapacitance(
            success=True,
            value=value,
            error_message=None,
            formatted=formatted
        )

    # 3. Try plain decimal (T041)
    value = _parse_plain_decimal(value_str)
    if value is not None:
        if value <= 0:
            return ParsedCapacitance(
                success=False,
                value=None,
                error_message="Capacitance must be positive",
                formatted=""
            )
        formatted = format_capacitance(value)
        return ParsedCapacitance(
            success=True,
            value=value,
            error_message=None,
            formatted=formatted
        )

    # Parsing failed
    return ParsedCapacitance(
        success=False,
        value=None,
        error_message=(
            f"Cannot parse '{value_str}'. "
            "Expected formats: '5.2pF', '1e-11', '1.2*10^-12', '0.000000000052'"
        ),
        formatted=""
    )


def _parse_with_unit_suffix(value_str: str) -> Optional[float]:
    """Parse capacitance with unit suffix (pF, nF, µF, uF, mF, F).

    Case-sensitive: F must be capital. Supports both µF and uF for microfarads.

    Args:
        value_str: Input string (e.g., "5.2pF", "1nF").

    Returns:
        Value in Farads, or None if no unit suffix found.

    Examples:
        >>> _parse_with_unit_suffix("5.2pF")
        5.2e-12
        >>> _parse_with_unit_suffix("1nF")
        1e-09
        >>> _parse_with_unit_suffix("2.7µF")
        2.7e-06
        >>> _parse_with_unit_suffix("2.7uF")
        2.7e-06
    """
    # Unit multipliers (order matters: check longer suffixes first)
    units = [
        ('pF', 1e-12),
        ('nF', 1e-9),
        ('µF', 1e-6),
        ('uF', 1e-6),  # Alternative for µ
        ('mF', 1e-3),
        ('F', 1.0),
    ]

    for unit, multiplier in units:
        if value_str.endswith(unit):
            number_part = value_str[:-len(unit)].strip()
            try:
                return float(number_part) * multiplier
            except ValueError:
                return None

    return None


def _parse_scientific_notation(value_str: str) -> Optional[float]:
    """Parse scientific or engineering notation.

    Supports:
    - Standard scientific: 1e-11, 1.2e-12, 5E-10
    - Engineering notation: 1*10^-11, 1.2*10^-12
    - Spaces allowed: 1 * 10 ^ -11

    Args:
        value_str: Input string.

    Returns:
        Value in Farads, or None if not scientific notation.

    Examples:
        >>> _parse_scientific_notation("1e-11")
        1e-11
        >>> _parse_scientific_notation("1.2e-12")
        1.2e-12
        >>> _parse_scientific_notation("1*10^-11")
        1e-11
        >>> _parse_scientific_notation("1.2 * 10 ^ -12")
        1.2e-12
    """
    # Try standard scientific notation (1e-11, 1.2E-12)
    try:
        value = float(value_str)
        # If it parses as float and contains 'e' or 'E', it's scientific
        if 'e' in value_str.lower():
            return value
    except ValueError:
        pass

    # Try engineering notation (1*10^-11, 1.2*10^-12)
    # Pattern: number * 10 ^ exponent
    pattern = r'^([-+]?\d+\.?\d*)\s*\*\s*10\s*\^\s*([-+]?\d+)$'
    match = re.match(pattern, value_str)
    if match:
        try:
            mantissa = float(match.group(1))
            exponent = int(match.group(2))
            return mantissa * (10 ** exponent)
        except (ValueError, OverflowError):
            return None

    return None


def _parse_plain_decimal(value_str: str) -> Optional[float]:
    """Parse plain decimal number (assumed to be in Farads).

    Args:
        value_str: Input string (e.g., "0.0000000001", "5.2").

    Returns:
        Value in Farads, or None if not a valid decimal.

    Examples:
        >>> _parse_plain_decimal("0.0000000001")
        1e-10
        >>> _parse_plain_decimal("5.2")
        5.2
    """
    try:
        return float(value_str)
    except ValueError:
        return None


def format_capacitance(value: float, precision: int = 3) -> str:
    """Format capacitance value to human-readable string with appropriate unit.

    Chooses unit based on magnitude:
    - < 1nF (1e-9): pF (picofarads)
    - 1nF to < 1µF (1e-6): nF (nanofarads)
    - 1µF to < 1mF (1e-3): µF (microfarads)
    - 1mF to < 1F: mF (millifarads)
    - >= 1F: F (farads)

    Args:
        value: Capacitance in Farads.
        precision: Number of significant figures (default 3).

    Returns:
        Formatted string with unit (e.g., "5.2pF", "1.5nF").

    Examples:
        >>> format_capacitance(5.2e-12)
        '5.2pF'
        >>> format_capacitance(1.5e-9)
        '1.5nF'
        >>> format_capacitance(2.7e-6)
        '2.7µF'
        >>> format_capacitance(1.0e-3)
        '1mF'
        >>> format_capacitance(1.0)
        '1F'
    """
    if value == 0:
        return "0F"

    abs_value = abs(value)

    # Choose appropriate unit based on magnitude
    if abs_value < 1e-9:  # < 1nF
        return f"{value * 1e12:.{precision}g}pF"
    elif abs_value < 1e-6:  # < 1µF
        return f"{value * 1e9:.{precision}g}nF"
    elif abs_value < 1e-3:  # < 1mF
        return f"{value * 1e6:.{precision}g}µF"
    elif abs_value < 1:  # < 1F
        return f"{value * 1e3:.{precision}g}mF"
    else:
        return f"{value:.{precision}g}F"

"""Unit tests for capacitance parsing and formatting.

Tests verify:
- Unit suffix parsing (pF, nF, µF, uF, mF, F)
- Scientific notation (1e-11, 1.2e-12)
- Engineering notation (1*10^-11, 1.2*10^-12)
- Plain decimals
- Edge cases (negative, zero, invalid, lowercase, very large/small)
- Format output with appropriate units

Constitutional Compliance:
    - Principle III (Robust Input): Comprehensive format coverage and error handling
"""

from __future__ import annotations
import pytest
from capassigner.core.parsing import (
    ParsedCapacitance,
    parse_capacitance,
    format_capacitance,
    _parse_with_unit_suffix,
    _parse_scientific_notation,
    _parse_plain_decimal
)


class TestUnitSuffixParsing:
    """Test parsing with unit suffixes (pF, nF, µF, uF, mF, F)."""

    def test_parse_picofarads(self):
        """Test parsing picofarads (pF)."""
        result = parse_capacitance("5.2pF")
        assert result.success is True
        assert abs(result.value - 5.2e-12) < 1e-20  # Floating-point tolerance
        assert result.error_message is None

    def test_parse_nanofarads(self):
        """Test parsing nanofarads (nF)."""
        result = parse_capacitance("1nF")
        assert result.success is True
        assert result.value == 1e-9

    def test_parse_microfarads_mu(self):
        """Test parsing microfarads with µ character (µF)."""
        result = parse_capacitance("2.7µF")
        assert result.success is True
        assert result.value == 2.7e-6

    def test_parse_microfarads_u(self):
        """Test parsing microfarads with u character (uF)."""
        result = parse_capacitance("2.7uF")
        assert result.success is True
        assert result.value == 2.7e-6

    def test_parse_millifarads(self):
        """Test parsing millifarads (mF)."""
        result = parse_capacitance("1mF")
        assert result.success is True
        assert result.value == 1e-3

    def test_parse_farads(self):
        """Test parsing farads (F)."""
        result = parse_capacitance("0.5F")
        assert result.success is True
        assert result.value == 0.5


class TestScientificNotation:
    """Test parsing scientific notation (1e-11, 1.2e-12)."""

    def test_parse_standard_scientific(self):
        """Test standard scientific notation (1e-11)."""
        result = parse_capacitance("1e-11")
        assert result.success is True
        assert result.value == 1e-11

    def test_parse_scientific_with_decimal(self):
        """Test scientific notation with decimal (1.2e-12)."""
        result = parse_capacitance("1.2e-12")
        assert result.success is True
        assert result.value == 1.2e-12

    def test_parse_scientific_uppercase_e(self):
        """Test scientific notation with uppercase E."""
        result = parse_capacitance("5E-10")
        assert result.success is True
        assert result.value == 5e-10

    def test_parse_engineering_notation(self):
        """Test engineering notation (1*10^-11)."""
        result = parse_capacitance("1*10^-11")
        assert result.success is True
        assert result.value == 1e-11

    def test_parse_engineering_with_decimal(self):
        """Test engineering notation with decimal (1.2*10^-12)."""
        result = parse_capacitance("1.2*10^-12")
        assert result.success is True
        assert result.value == 1.2e-12

    def test_parse_engineering_with_spaces(self):
        """Test engineering notation with spaces (1 * 10 ^ -11)."""
        result = parse_capacitance("1 * 10 ^ -11")
        assert result.success is True
        assert result.value == 1e-11


class TestPlainDecimals:
    """Test parsing plain decimal numbers."""

    def test_parse_small_decimal(self):
        """Test parsing very small decimal (0.0000000001)."""
        result = parse_capacitance("0.0000000001")
        assert result.success is True
        assert result.value == 1e-10

    def test_parse_simple_decimal(self):
        """Test parsing simple decimal (5.2)."""
        result = parse_capacitance("5.2")
        assert result.success is True
        assert result.value == 5.2

    def test_parse_integer(self):
        """Test parsing integer."""
        result = parse_capacitance("3")
        assert result.success is True
        assert result.value == 3.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_negative_value_rejected(self):
        """Test that negative values are rejected."""
        result = parse_capacitance("-5pF")
        assert result.success is False
        assert "positive" in result.error_message.lower()

    def test_zero_value_rejected(self):
        """Test that zero values are rejected."""
        result = parse_capacitance("0pF")
        assert result.success is False
        assert "positive" in result.error_message.lower()

    def test_lowercase_f_rejected(self):
        """Test that lowercase 'f' is rejected."""
        result = parse_capacitance("5pf")
        assert result.success is False
        assert "capital F" in result.error_message

    def test_lowercase_nf_rejected(self):
        """Test that lowercase 'nf' is rejected."""
        result = parse_capacitance("5nf")
        assert result.success is False
        assert "capital F" in result.error_message

    def test_invalid_format(self):
        """Test invalid format returns error."""
        result = parse_capacitance("abc")
        assert result.success is False
        assert "Cannot parse" in result.error_message

    def test_very_large_value(self):
        """Test very large capacitance value."""
        result = parse_capacitance("1000F")
        assert result.success is True
        assert result.value == 1000.0

    def test_very_small_value(self):
        """Test very small capacitance value (femtofarads scale)."""
        result = parse_capacitance("1e-15")
        assert result.success is True
        assert result.value == 1e-15

    def test_whitespace_handling(self):
        """Test that leading/trailing whitespace is handled."""
        result = parse_capacitance("  5.2pF  ")
        assert result.success is True
        assert abs(result.value - 5.2e-12) < 1e-20  # Floating-point tolerance


class TestFormattedOutput:
    """Test that formatted string is generated correctly."""

    def test_formatted_output_picofarads(self):
        """Test formatted output for picofarads."""
        result = parse_capacitance("5.2pF")
        assert "pF" in result.formatted

    def test_formatted_output_scientific(self):
        """Test formatted output for scientific notation."""
        result = parse_capacitance("1e-11")
        assert result.formatted  # Should have some formatted output
        # Value is 10pF, so should format as pF
        assert "pF" in result.formatted


class TestFormatCapacitance:
    """Test format_capacitance function."""

    def test_format_picofarads(self):
        """Test formatting picofarads."""
        formatted = format_capacitance(5.2e-12)
        assert formatted == "5.2pF"

    def test_format_nanofarads(self):
        """Test formatting nanofarads."""
        formatted = format_capacitance(1.5e-9)
        assert formatted == "1.5nF"

    def test_format_microfarads(self):
        """Test formatting microfarads."""
        formatted = format_capacitance(2.7e-6)
        assert formatted == "2.7µF"

    def test_format_millifarads(self):
        """Test formatting millifarads."""
        formatted = format_capacitance(1.0e-3)
        assert formatted == "1mF"

    def test_format_farads(self):
        """Test formatting farads."""
        formatted = format_capacitance(1.0)
        assert formatted == "1F"

    def test_format_zero(self):
        """Test formatting zero."""
        formatted = format_capacitance(0.0)
        assert formatted == "0F"

    def test_format_precision(self):
        """Test formatting with custom precision."""
        formatted = format_capacitance(5.12345e-12, precision=2)
        # Should have 2 significant figures
        assert "pF" in formatted

    def test_format_very_small(self):
        """Test formatting very small value."""
        formatted = format_capacitance(1e-15)
        assert "pF" in formatted  # Should use pF for femtofarad scale

    def test_format_boundary_values(self):
        """Test formatting at unit boundaries."""
        # Exactly 1nF (boundary between pF and nF)
        formatted_1nf = format_capacitance(1e-9)
        assert "nF" in formatted_1nf

        # Exactly 1µF (boundary between nF and µF)
        formatted_1uf = format_capacitance(1e-6)
        assert "µF" in formatted_1uf


class TestHelperFunctions:
    """Test internal helper functions."""

    def test_parse_with_unit_suffix_valid(self):
        """Test _parse_with_unit_suffix with valid input."""
        value = _parse_with_unit_suffix("5.2pF")
        assert abs(value - 5.2e-12) < 1e-20  # Floating-point tolerance

    def test_parse_with_unit_suffix_invalid(self):
        """Test _parse_with_unit_suffix with invalid input."""
        value = _parse_with_unit_suffix("5.2")
        assert value is None

    def test_parse_scientific_notation_valid(self):
        """Test _parse_scientific_notation with valid input."""
        value = _parse_scientific_notation("1e-11")
        assert value == 1e-11

    def test_parse_scientific_notation_invalid(self):
        """Test _parse_scientific_notation with invalid input."""
        value = _parse_scientific_notation("5.2pF")
        assert value is None

    def test_parse_plain_decimal_valid(self):
        """Test _parse_plain_decimal with valid input."""
        value = _parse_plain_decimal("5.2")
        assert value == 5.2

    def test_parse_plain_decimal_invalid(self):
        """Test _parse_plain_decimal with invalid input."""
        value = _parse_plain_decimal("abc")
        assert value is None


class TestMixedFormats:
    """Test integration scenario with mixed formats (from User Story 2)."""

    def test_user_story_2_scenario(self):
        """Test User Story 2: Mixed formats "5.2pF, 1e-11, 0.000000000012, 10*10^-12"."""
        inputs = ["5.2pF", "1e-11", "0.000000000012", "10*10^-12"]
        # 5.2pF = 5.2e-12
        # 1e-11 = 1e-11
        # 0.000000000012 = 12e-12 = 1.2e-11
        # 10*10^-12 = 10e-12 = 1e-11
        expected_values = [5.2e-12, 1e-11, 1.2e-11, 1e-11]

        for input_str, expected in zip(inputs, expected_values):
            result = parse_capacitance(input_str)
            assert result.success is True
            assert abs(result.value - expected) < 1e-20  # Floating point tolerance

    def test_all_formats_display_correctly(self):
        """Test that all formats produce human-readable display."""
        inputs = ["5.2pF", "1e-11", "0.000000000012"]

        for input_str in inputs:
            result = parse_capacitance(input_str)
            assert result.success is True
            assert result.formatted  # Non-empty
            assert any(unit in result.formatted for unit in ["pF", "nF", "µF", "mF", "F"])


class TestDataclass:
    """Test ParsedCapacitance dataclass."""

    def test_dataclass_structure(self):
        """Test ParsedCapacitance has correct structure."""
        result = ParsedCapacitance(
            success=True,
            value=5.2e-12,
            error_message=None,
            formatted="5.2pF"
        )

        assert result.success is True
        assert result.value == 5.2e-12
        assert result.error_message is None
        assert result.formatted == "5.2pF"

    def test_dataclass_failure(self):
        """Test ParsedCapacitance for failure case."""
        result = ParsedCapacitance(
            success=False,
            value=None,
            error_message="Invalid format",
            formatted=""
        )

        assert result.success is False
        assert result.value is None
        assert result.error_message == "Invalid format"
        assert result.formatted == ""

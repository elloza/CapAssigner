"""Pytest configuration and shared fixtures.

This module provides pytest configuration, shared fixtures, and test setup
for the CapAssigner test suite.
"""

import pytest


@pytest.fixture
def sample_capacitors():
    """Provide sample capacitor list for tests.

    Returns:
        List of capacitor values in Farads.
    """
    return [1e-12, 2e-12, 5e-12, 10e-12]


@pytest.fixture
def sample_names():
    """Provide sample capacitor names for tests.

    Returns:
        List of capacitor names matching sample_capacitors.
    """
    return ["C1", "C2", "C3", "C4"]


# Add more shared fixtures as needed

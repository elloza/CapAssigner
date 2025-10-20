"""Centralized tooltip text for UI widgets.

This module contains all help text (tooltips) for Streamlit widgets,
ensuring consistency and easy maintenance of user-facing documentation.

This is a placeholder module created during scaffolding.
Implementation details will be added in subsequent features.
"""

# Capacitor input tooltips
TOOLTIP_CAP_LIST = """
Enter capacitor values with units (pF, nF, µF, mF, F).
Supports scientific notation: 1e-11, 1.2*10^-12
"""

TOOLTIP_CAP_TARGET = """
Target equivalent capacitance. Accepts same formats as capacitor list.
Example: 5.2pF, 0.1µF, 1e-11
"""

TOOLTIP_TOLERANCE = """
Absolute tolerance (margin of error) for matching the target.
Default: 1% of target capacitance.
"""

# Method selection tooltips
TOOLTIP_METHOD_SIMPLE = """
Fast two-level series-parallel combinations.
Suitable for quick approximations with any number of capacitors.
"""

TOOLTIP_METHOD_SP_EXHAUSTIVE = """
Exhaustive enumeration of all series-parallel topologies.
Exact solution for SP networks, but limited to N ≤ 8 capacitors.
Complexity: ≈ Catalan(N) × N!
"""

TOOLTIP_METHOD_HEURISTIC = """
Heuristic search for general (non-SP) network topologies.
Can handle bridges, meshes, and internal nodes.
Recommended for N > 8 or when SP search is too slow.
"""

TOOLTIP_MAX_N_SP = """
Maximum number of capacitors for exhaustive SP enumeration.
Higher values may cause long computation times.
Constitutional default: 8
"""

# Heuristic parameters
TOOLTIP_HEURISTIC_ITERS = """
Number of random topologies to evaluate.
More iterations = better coverage, but longer execution time.
Constitutional default: 2000
"""

TOOLTIP_HEURISTIC_INTERNAL = """
Maximum number of internal nodes (besides terminals A and B).
More nodes = more expressive networks, but higher complexity.
Constitutional default: 2
"""

TOOLTIP_SEED = """
Random seed for reproducible results.
Same seed → same heuristic output.
Constitutional default: 0
"""

# UI appearance
TOOLTIP_UI_SCALE = """
Global UI scaling factor.
Adjusts text size and widget dimensions.
"""

TOOLTIP_DIAGRAM_SCALE = """
Scaling factor for circuit diagrams and graphs.
Larger values = bigger visualizations.
"""


def get_tooltip(key: str) -> str:
    """Retrieve tooltip text by key.

    Args:
        key: Tooltip identifier (e.g., 'CAP_LIST', 'METHOD_SP').

    Returns:
        Tooltip text string, or empty string if key not found.

    Example:
        >>> get_tooltip('TOOLTIP_CAP_TARGET')
        'Target equivalent capacitance. Accepts same formats...'
    """
    # Placeholder implementation
    return globals().get(f"TOOLTIP_{key}", "")

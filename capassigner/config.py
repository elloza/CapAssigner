"""Configuration constants for CapAssigner.

This module defines application-wide constants that reflect the
constitutional principles defined in .specify/memory/constitution.md

Constitutional Alignment:
    - I. Scientific Accuracy: Precision and validation thresholds
    - II. User Experience First: Default UI parameters
    - III. Robust Input Handling: Input validation limits
    - IV. Modular Architecture: Import restrictions enforced
    - V. Performance Awareness: Computational limits
    - VI. Educational Transparency: Documentation flags
"""

from typing import Tuple

# Use typing_extensions.Final for Python <3.8 compatibility
try:
    from typing import Final
except ImportError:
    from typing_extensions import Final

# ============================================================================
# Scientific Accuracy (Principle I)
# ============================================================================

# Default tolerance for capacitance matching (percentage, ±5%)
DEFAULT_TOLERANCE: Final[float] = 5.0

# Minimum allowed tolerance (percentage, 0.1%)
MIN_TOLERANCE: Final[float] = 0.1

# Maximum allowed tolerance (percentage, 50%)
MAX_TOLERANCE: Final[float] = 50.0

# Numerical precision for float comparisons (1 femtofarad)
EPSILON: Final[float] = 1e-15


# ============================================================================
# User Experience First (Principle II)
# ============================================================================

# Default page layout
DEFAULT_PAGE_LAYOUT: Final[str] = "wide"

# Application icon
APP_ICON: Final[str] = "🔌"

# Application title
APP_TITLE: Final[str] = "CapAssigner"

# Application subtitle
APP_SUBTITLE: Final[str] = "Capacitor Network Synthesis"


# ============================================================================
# Robust Input Handling (Principle III)
# ============================================================================

# Maximum number of capacitors in inventory
MAX_INVENTORY_SIZE: Final[int] = 1000

# Minimum capacitance value (1 femtofarad)
MIN_CAPACITANCE: Final[float] = 1e-15

# Maximum capacitance value (1 Farad)
MAX_CAPACITANCE: Final[float] = 1.0

# Maximum target capacitance value (1 Farad)
MAX_TARGET_CAPACITANCE: Final[float] = 1.0

# Supported capacitance units
CAPACITANCE_UNITS: Final[Tuple[str, ...]] = (
    "F",   # Farad
    "mF",  # millifarad
    "uF",  # microfarad
    "nF",  # nanofarad
    "pF",  # picofarad
    "fF",  # femtofarad
)


# ============================================================================
# Performance Awareness (Principle V)
# ============================================================================

# Maximum number of capacitors for SP exhaustive enumeration (Catalan(N) × N!)
MAX_SP_EXHAUSTIVE_N: Final[int] = 8

# Default number of iterations for heuristic graph search
DEFAULT_HEURISTIC_ITERS: Final[int] = 2000

# Default maximum internal nodes for heuristic graph generation
DEFAULT_MAX_INTERNAL_NODES: Final[int] = 2

# Maximum number of iterations for heuristic algorithms
MAX_HEURISTIC_ITERATIONS: Final[int] = 10000

# Default population size for genetic algorithms (future enhancement)
DEFAULT_GA_POPULATION: Final[int] = 100

# Default number of solutions to display
DEFAULT_NUM_SOLUTIONS: Final[int] = 10

# Progress callback update frequency (every N iterations)
PROGRESS_UPDATE_FREQUENCY: Final[int] = 50


# ============================================================================
# Educational Transparency (Principle VI)
# ============================================================================

# Enable educational tooltips by default
ENABLE_TOOLTIPS: Final[bool] = True

# Enable theoretical explanations by default
ENABLE_THEORY: Final[bool] = True

# Show algorithm complexity warnings
SHOW_COMPLEXITY_WARNINGS: Final[bool] = True


# ============================================================================
# E-Series Standard Values (T089)
# ============================================================================

# E12 series (12 values per decade, ±10% tolerance)
E12_SERIES: Final[Tuple[float, ...]] = (
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2
)

# E24 series (24 values per decade, ±5% tolerance)
E24_SERIES: Final[Tuple[float, ...]] = (
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
)

# E48 series (48 values per decade, ±2% tolerance)
E48_SERIES: Final[Tuple[float, ...]] = (
    1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
    1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
    3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
    5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53
)

# E96 series (96 values per decade, ±1% tolerance)
E96_SERIES: Final[Tuple[float, ...]] = (
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76
)


# ============================================================================
# Module Import Restrictions (Principle IV)
# ============================================================================

# Modules that MUST NOT import streamlit
STREAMLIT_FORBIDDEN_MODULES: Final[Tuple[str, ...]] = (
    "capassigner.core.parsing",
    "capassigner.core.sp_structures",
    "capassigner.core.sp_enumeration",
    "capassigner.core.graphs",
    "capassigner.core.heuristics",
    "capassigner.core.metrics",
)

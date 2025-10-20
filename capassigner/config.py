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

from typing import Final, Tuple

# ============================================================================
# Scientific Accuracy (Principle I)
# ============================================================================

# Default tolerance for capacitance matching (5%)
DEFAULT_TOLERANCE: Final[float] = 0.05

# Minimum allowed tolerance (0.1%)
MIN_TOLERANCE: Final[float] = 0.001

# Maximum allowed tolerance (50%)
MAX_TOLERANCE: Final[float] = 0.50

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

# Maximum number of capacitors for brute-force SP enumeration
MAX_BRUTE_FORCE_SIZE: Final[int] = 7

# Maximum number of iterations for heuristic algorithms
MAX_HEURISTIC_ITERATIONS: Final[int] = 10000

# Default population size for genetic algorithms
DEFAULT_GA_POPULATION: Final[int] = 100

# Default number of solutions to display
DEFAULT_NUM_SOLUTIONS: Final[int] = 10

# Progress callback update frequency (every N iterations)
PROGRESS_UPDATE_FREQUENCY: Final[int] = 100


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

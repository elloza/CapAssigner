"""CapAssigner - Capacitor Network Synthesis Application.

A modular Streamlit application for synthesizing capacitor networks
that achieve target capacitance values within specified tolerances.

Architecture:
    - core/: Pure computational modules (NO Streamlit dependencies)
    - ui/: Streamlit-based user interface modules

Constitutional Principles:
    I. Scientific Accuracy
    II. User Experience First
    III. Robust Input Handling
    IV. Modular Architecture
    V. Performance Awareness
    VI. Educational Transparency
"""

__version__ = "0.1.0"
__author__ = "CapAssigner Team"

# Re-export core functionality for convenience
from capassigner.core import graphs, heuristics, metrics, parsing, sp_enumeration, sp_structures

__all__ = [
    "graphs",
    "heuristics",
    "metrics",
    "parsing",
    "sp_enumeration",
    "sp_structures",
    "__version__",
    "__author__",
]

"""User Interface modules for CapAssigner.

This package contains Streamlit-based UI components.
Streamlit imports ARE ALLOWED in this package.

Modules:
    - pages: Main application pages and navigation
    - theory: Educational content and theoretical explanations
    - plots: Visualization utilities (SchemDraw, NetworkX, Matplotlib)
    - tooltips: Centralized tooltip and help text constants

Design Principles:
    - Follow Constitutional Principle II: User Experience First
    - All UI modules may import from capassigner.core
    - All UI modules may import streamlit
    - Keep UI logic separate from computational logic
"""

from capassigner.ui import pages, plots, theory, tooltips

__all__ = [
    "pages",
    "plots",
    "theory",
    "tooltips",
]

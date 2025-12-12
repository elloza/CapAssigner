# CapAssigner Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-20

## Active Technologies
- Python 3.9+ (requires modern type hints, pathlib, dataclasses) + Streamlit (UI framework), NumPy (numerical operations), Pandas (data handling), Matplotlib (plotting), NetworkX (graph visualization), SchemDraw (circuit diagrams) (001-app-scaffolding)
- Python 3.9+ (requires modern type hints per PEP 484, 585, 604; pathlib; dataclasses) + Streamlit (UI framework), NumPy (numerical operations, matrix solving), Pandas (data handling for results tables), Matplotlib (plotting), NetworkX (graph visualization and topology representation), SchemDraw (circuit diagram rendering) (002-full-app-implementation)
- Session state only (st.session_state); no persistent database required for MVP (002-full-app-implementation)

## Project Structure
```
src/
tests/
```

## Commands
cd src; pytest; ruff check .

## Code Style
Python 3.9+ (requires modern type hints, pathlib, dataclasses): Follow standard conventions

## Recent Changes
- 006-lcapy-visualization (2025-12-12): Integrated lcapy library for professional CircuiTikZ-quality circuit diagrams. Added netlist conversion functions, updated render_sp_circuit() and render_graph_network() with lcapy as primary renderer and fallback to schemdraw/matplotlib. Fixed Exercise 02 disconnected terminal visualization. **BUG FIXES** (same day): Fixed TypeError with regular Graph (added MultiGraph detection), Fixed lcapy value format (changed from "15uF" to "1.5e-05" scientific notation). All 14 tests passing.
- 002-full-app-implementation: Added Python 3.9+ (requires modern type hints per PEP 484, 585, 604; pathlib; dataclasses) + Streamlit (UI framework), NumPy (numerical operations, matrix solving), Pandas (data handling for results tables), Matplotlib (plotting), NetworkX (graph visualization and topology representation), SchemDraw (circuit diagram rendering)
- 001-app-scaffolding: Added Python 3.9+ (requires modern type hints, pathlib, dataclasses) + Streamlit (UI framework), NumPy (numerical operations), Pandas (data handling), Matplotlib (plotting), NetworkX (graph visualization), SchemDraw (circuit diagrams)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

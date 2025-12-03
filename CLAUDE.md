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
- 002-full-app-implementation: Added Python 3.9+ (requires modern type hints per PEP 484, 585, 604; pathlib; dataclasses) + Streamlit (UI framework), NumPy (numerical operations, matrix solving), Pandas (data handling for results tables), Matplotlib (plotting), NetworkX (graph visualization and topology representation), SchemDraw (circuit diagram rendering)
- 001-app-scaffolding: Added Python 3.9+ (requires modern type hints, pathlib, dataclasses) + Streamlit (UI framework), NumPy (numerical operations), Pandas (data handling), Matplotlib (plotting), NetworkX (graph visualization), SchemDraw (circuit diagrams)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

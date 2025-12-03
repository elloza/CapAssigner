# Quickstart: CapAssigner Development Setup

**Purpose**: Get a new developer from zero to running the CapAssigner application in under 10 minutes.

**Target Audience**: Developers joining the CapAssigner project or setting up on a new machine.

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Git** (version 2.0+) - [Download](https://git-scm.com/downloads)
- ✅ **Conda** (Miniconda or Anaconda) - [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- ✅ **Code Editor** with Python support (VS Code, PyCharm, or similar)

**Operating Systems Supported**: Windows, Linux, macOS

---

## Step 1: Clone Repository (1 minute)

```bash
# Clone the repository
git clone https://github.com/<org>/CapAssigner.git
cd CapAssigner

# Verify you're on the scaffolding branch (if implementing this feature)
git branch
# Should show: * 001-app-scaffolding
```

**Checkpoint**: You should see the repository structure with `capassigner/`, `tests/`, `app.py`, etc.

---

## Step 2: Create Conda Environment (2 minutes)

**IMPORTANT**: This project uses a conda environment at `.conda/` in the project root.

```bash
# Create conda environment with Python 3.9
conda create --prefix ./.conda python=3.9

# Activate the environment
conda activate ./.conda

# Verify Python version
python --version
# Should show: Python 3.9.x
```

**Troubleshooting**:
- If `conda activate ./.conda` fails, try: `conda activate ./. conda` (with space) or use the full path
- On Windows, you may need to run: `conda init powershell` or `conda init cmd.exe` first
- On Linux/Mac with bash: `conda init bash` then restart your shell

**Checkpoint**: Your terminal prompt should now show `(.conda)` prefix.

---

## Step 3: Install Dependencies (2 minutes)

```bash
# Ensure conda environment is activated
# You should see (.conda) in your prompt

# Install project dependencies via pip
pip install -r requirements.txt

# Verify installation
pip list | grep streamlit
# Should show streamlit version (e.g., streamlit==1.28.0)
```

**What Gets Installed**:
- **Streamlit** - Web UI framework
- **NumPy** - Numerical computing
- **Pandas** - Data handling
- **Matplotlib** - Plotting backend
- **NetworkX** - Graph visualization
- **SchemDraw** - Circuit diagram drawing
- **Development Tools**: pytest, mypy, ruff, black, isort

**Checkpoint**: `pip list` should show ~15-20 packages installed.

---

## Step 4: Run the Application (1 minute)

```bash
# Ensure conda environment is activated
streamlit run app.py
```

**Expected Output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**What You Should See**:
- Browser opens automatically to `http://localhost:8501`
- Placeholder page with "CapAssigner" title and welcome message
- Sidebar with navigation (may be empty for scaffolding)

**Checkpoint**: Application runs without errors, page loads in browser.

---

## Step 5: Verify Code Quality Tools (2 minutes)

```bash
# Run linter (ruff)
ruff check capassigner/

# Run formatter check (black)
black --check capassigner/

# Run import sorter check (isort)
isort --check capassigner/

# Run type checker (mypy)
mypy capassigner/

# Run tests (pytest)
pytest
```

**Expected Output**: All checks should **PASS** with zero errors on the scaffolding.

**Troubleshooting**:
- If tools are not found, verify conda environment is activated
- If checks fail, the scaffolding may not be complete yet

**Checkpoint**: All quality tools run successfully.

---

## Step 6: Optional - Install Pre-commit Hooks (1 minute)

Pre-commit hooks automatically run quality checks before each commit.

```bash
# Install pre-commit hooks
pre-commit install

# Test hooks manually
pre-commit run --all-files
```

**Expected Output**: All hooks pass (same as Step 5).

**Benefits**:
- Catches issues **before** they reach CI/CD
- Ensures consistent code style across team
- Saves time in code reviews

---

## Development Workflow

### Daily Work

```bash
# 1. Activate conda environment (every new terminal session)
conda activate ./.conda

# 2. Pull latest changes
git pull origin main

# 3. Create feature branch
git checkout -b 002-your-feature-name

# 4. Make changes to code

# 5. Run application to test
streamlit run app.py

# 6. Run quality checks (optional if pre-commit installed)
pre-commit run --all-files

# 7. Commit changes
git add .
git commit -m "feat: add your feature"

# 8. Push branch
git push origin 002-your-feature-name
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test type
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=capassigner

# Run with markers
pytest -m unit  # Only unit tests
```

### Code Quality

```bash
# Auto-fix issues
ruff check --fix capassigner/
black capassigner/
isort capassigner/

# Type check
mypy capassigner/
```

---

## Project Structure Quick Reference

```
CapAssigner/
├── .conda/                 # Conda environment (DO NOT COMMIT)
├── capassigner/            # Main package
│   ├── core/              # Pure computation (NO streamlit imports)
│   │   ├── parsing.py     # Capacitance parsing
│   │   ├── sp_structures.py
│   │   ├── sp_enumeration.py
│   │   ├── graphs.py
│   │   ├── heuristics.py
│   │   └── metrics.py
│   ├── ui/                # Streamlit UI components
│   │   ├── pages.py       # Main UI layouts
│   │   ├── theory.py      # Educational content
│   │   ├── plots.py       # Visualizations
│   │   └── tooltips.py    # Help text
│   └── config.py          # Constants and configuration
├── tests/                 # Test suite
│   ├── unit/             # Fast, isolated tests
│   ├── integration/      # Module interaction tests
│   └── contract/         # API stability tests
├── app.py                # Streamlit entry point
├── requirements.txt      # Python dependencies
└── environment.yml       # Conda environment spec
```

**Key Principles** (from constitution):
- `core/` modules **MUST NOT** import `streamlit`
- All functions **MUST** have type hints and docstrings
- Use `pathlib.Path` for all file paths (cross-platform)
- Immutable constants in `config.py`, mutable state in `st.session_state`

---

## Common Tasks

### Adding a New Core Module

```python
# capassigner/core/new_module.py
"""Brief description of what this module does.

Longer explanation if needed.
"""

from __future__ import annotations
from typing import Any, Callable


def new_function(
    arg: str,
    progress_cb: Callable[[int, int], None] | None = None
) -> dict[str, Any]:
    """Function description.

    Args:
        arg: Argument description
        progress_cb: Optional callback for progress updates (current, total)

    Returns:
        Dictionary with results

    Raises:
        ValueError: If arg is invalid
    """
    if progress_cb:
        progress_cb(1, 2)  # Report progress to UI

    result = {"status": "ok"}
    return result
```

### Adding a New UI Component

```python
# capassigner/ui/new_component.py
"""UI component for displaying XYZ."""

import streamlit as st
from capassigner.core.new_module import new_function


def render_new_component() -> None:
    """Render the new UI component.

    Uses Streamlit session state for managing user input.
    """
    st.header("New Component")

    # Initialize session state
    if "new_key" not in st.session_state:
        st.session_state.new_key = ""

    # Widget with unique key
    user_input = st.text_input(
        "Enter value",
        key="new_key",
        help="Tooltip text here"
    )

    if st.button("Process"):
        result = new_function(user_input)
        st.success(f"Result: {result}")
```

### Adding Tests

```python
# tests/unit/test_new_module.py
"""Unit tests for new_module."""

import pytest
from capassigner.core.new_module import new_function


def test_new_function_basic():
    """Test new_function with valid input."""
    result = new_function("valid")
    assert result["status"] == "ok"


def test_new_function_invalid():
    """Test new_function with invalid input."""
    with pytest.raises(ValueError):
        new_function("")
```

---

## Troubleshooting

### Conda Environment Issues

**Problem**: `conda activate ./.conda` doesn't work

**Solutions**:
```bash
# Try with full path
conda activate /full/path/to/CapAssigner/.conda

# Or recreate environment
conda env remove --prefix ./.conda
conda create --prefix ./.conda python=3.9
```

### Streamlit Port Already in Use

**Problem**: `Address already in use` error

**Solutions**:
```bash
# Use different port
streamlit run app.py --server.port 8502

# Kill existing Streamlit process (Linux/Mac)
pkill -f streamlit

# Kill existing Streamlit process (Windows)
taskkill /F /IM streamlit.exe
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'capassigner'`

**Solutions**:
```bash
# Ensure you're in the project root
cd /path/to/CapAssigner

# Ensure conda environment is activated
conda activate ./.conda

# Reinstall dependencies
pip install -r requirements.txt
```

### Type Checking Errors

**Problem**: mypy reports errors in placeholder modules

**Solution**: This is expected during scaffolding. Placeholder modules may have intentionally incomplete implementations. Check `research.md` for mypy configuration details.

---

## Next Steps

After completing this quickstart:

1. ✅ **Read the Constitution** - `.specify/memory/constitution.md` for core principles
2. ✅ **Review the Spec** - `specs/001-app-scaffolding/spec.md` for feature requirements
3. ✅ **Check the Plan** - `specs/001-app-scaffolding/plan.md` for implementation strategy
4. ✅ **Explore the Code** - Browse `capassigner/` to understand structure
5. ✅ **Run Tests** - `pytest -v` to see test structure

**Questions?** Check the main `README.md` or open an issue on GitHub.

---

## Summary

You should now have:
- ✅ Conda environment activated at `.conda/`
- ✅ All dependencies installed
- ✅ Application running at `http://localhost:8501`
- ✅ All code quality tools passing
- ✅ Understanding of project structure

**Total Time**: ~10 minutes

**You're ready to start developing!** 🚀

# CapAssigner Quickstart Guide

**Version**: 1.0.0
**Feature**: 002-full-app-implementation
**Date**: 2025-10-20

## Overview

CapAssigner is a web-based tool for designing capacitor networks that achieve target capacitance values. It supports:
- **Series-Parallel (SP) Exhaustive**: Finds all SP topologies for small networks (N≤8)
- **Heuristic Graph Search**: Explores general topologies (including non-SP) using random generation

This guide covers installation, basic usage, and result interpretation.

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip or conda package manager

### Option 1: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/CapAssigner.git
cd CapAssigner

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using conda

```bash
# Clone the repository
git clone https://github.com/yourusername/CapAssigner.git
cd CapAssigner

# Create conda environment
conda env create -f environment.yml
conda activate capassigner
```

### Verify Installation

```bash
# Test import
python -c "import capassigner; print('✓ CapAssigner installed successfully')"

# Run tests (optional)
pytest -v
```

---

## Running the Application

### Start the Streamlit App

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

---

## Basic Usage

### Step 1: Enter Target Capacitance

In the **Target Capacitance** input field, enter your desired capacitance value using any of these formats:

**Supported Formats**:
- Unit suffixes: `5.2pF`, `1.23nF`, `4.7µF` (or `4.7uF`), `100mF`, `1F`
- Scientific notation: `1e-11`, `1.2e-12`, `5.2*10^-12`
- Plain decimals: `0.0000000052` (will be converted to 5.2pF)

**Examples**:
- `3.1pF` → 3.1 picofarads
- `2.5nF` → 2.5 nanofarads
- `1e-11` → 10 picofarads

**Important**:
- Use capital `F` for Farad (lowercase `pf` will fail)
- Target must be positive (negative or zero values are rejected)

---

### Step 2: Add Capacitors to Inventory

Build your capacitor inventory using the **Capacitor Inventory** table:

**Methods**:
1. **Manual Entry**: Click "Add Row" and enter capacitance values directly in the table
2. **Load Preset**: Click one of the preset buttons (E12, E24, E48, E96) to load standard capacitor series
3. **Edit/Remove**: Click on a row to edit values, or select and click "Remove" to delete

**Format**:
- Enter capacitance values using the same formats as target (e.g., `5.2pF`, `1e-11`)
- Values are converted to Farads internally but displayed in human-readable format

**Example Inventory**:
```
C1: 1pF
C2: 2pF
C3: 5pF
C4: 10pF
```

---

### Step 3: Select Search Method

Choose between two algorithms:

#### Option A: SP Exhaustive (Recommended for N≤8)

**Best For**: Small inventories (≤8 capacitors), finding all possible series-parallel solutions

**How It Works**:
- Enumerates all series-parallel topologies (connections using only series and parallel)
- Uses dynamic programming with memoization for efficiency
- Guarantees finding all SP solutions

**Performance**:
- N=5: ~1 second, ~100 topologies
- N=8: ~3 seconds, ~10,000 topologies
- N>8: **Warning displayed** ("May be slow; consider Heuristic method")

**When to Use**:
- You have 8 or fewer capacitors
- You want to see all possible SP combinations
- You need guaranteed optimal SP solution

---

#### Option B: Heuristic Graph Search

**Best For**: Large inventories (>8 capacitors), exploring non-SP topologies (e.g., bridge networks)

**How It Works**:
- Generates random graph topologies with specified number of internal nodes
- Evaluates each using Laplacian-based nodal analysis
- Returns best solutions found during search

**Parameters**:
- **Iterations**: Number of random graphs to generate (default 2000)
  - More iterations → more exploration → better chance of finding good solution
  - Typical range: 1000-5000
- **Max Internal Nodes**: Complexity of networks (default 2)
  - 0: Only A and B (simple parallel/series)
  - 1: A, B, plus 1 internal node
  - 2: A, B, plus up to 2 internal nodes (enables bridge networks)
  - Higher values → more complex topologies but slower computation
- **Random Seed**: For reproducibility (default 0)
  - Same seed → same results (useful for debugging)
  - Different seeds → different exploration paths

**Performance**:
- 2000 iterations with 2 internal nodes: ~5-10 seconds

**When to Use**:
- You have more than 8 capacitors
- SP exhaustive would be too slow
- You want to explore non-SP topologies (e.g., bridge networks)

---

### Step 4: Set Tolerance (Optional)

**Tolerance** defines the acceptable error range as a percentage (±%).

**Default**: ±5%

**Examples**:
- Tolerance = 5%: Solutions within ±5% of target are marked as "within tolerance"
- Tolerance = 1%: Stricter requirement (only solutions within ±1% are marked)

**Use Case**:
- Filter results to show only solutions meeting your tolerance requirement
- Helps quickly identify acceptable solutions

---

### Step 5: Find Solutions

Click **"Find Solutions"** button.

**What Happens**:
1. **Validation**: System checks that target and inventory are valid
   - If errors exist, they are displayed with actionable messages
2. **Progress Feedback**: For operations >1 second, a progress bar appears with:
   - Current iteration count
   - Total topologies to explore
   - Best error found so far (for heuristic search)
3. **Results Display**: Solutions are shown in a sortable table

---

## Interpreting Results

### Results Table

Each solution row shows:

| Column | Description | Example |
|--------|-------------|---------|
| **Topology** | Network structure expression | `((C1\|\|C2)+C3)` |
| **C_eq** | Equivalent capacitance | `3.12pF` |
| **Abs Error** | \|C_eq - C_target\| | `0.02pF` |
| **Rel Error** | (Abs Error / Target) × 100% | `0.65%` |
| **Tolerance** | ✓ (within) or ✗ (outside) | ✓ |

**Sorting**:
- Results are pre-sorted by absolute error (best match first)
- Click column headers to re-sort

**Filtering**:
- Toggle "Show only within tolerance" to hide out-of-tolerance solutions

---

### Topology Expressions

**Series-Parallel Notation**:
- `C1`: Single capacitor
- `(C1+C2)`: C1 and C2 in series
- `(C1||C2)`: C1 and C2 in parallel
- `((C1||C2)+C3)`: C1 parallel with C2, then in series with C3

**Graph Networks**:
- Displayed as "Graph network with N nodes and M edges"
- View NetworkX diagram by expanding the row

---

### Circuit Diagrams

**Viewing Diagrams**:
1. Expand a solution row in the results table
2. Diagram is generated and displayed:
   - **SP topologies**: SchemDraw circuit diagram with labeled components
   - **Graph topologies**: NetworkX graph with nodes and edges

**Diagram Features**:
- **Components**: Labeled with name and value (e.g., "C1=5.2pF")
- **Terminals**: Marked as A and B
- **Clarity**: Professional-quality rendering

**Use Cases**:
- Verify topology structure
- Copy diagram for documentation
- Understand how capacitors are connected

---

## Understanding Errors

### Error Metrics

**Absolute Error**:
- Formula: `|C_eq - C_target|`
- Units: Same as capacitance (Farads, displayed as pF/nF/etc.)
- **Lower is better**
- Example: Target=3.1pF, C_eq=3.12pF → Abs Error=0.02pF

**Relative Error**:
- Formula: `(|C_eq - C_target| / C_target) × 100%`
- Units: Percentage
- **Lower is better**
- Example: Target=3.1pF, C_eq=3.12pF → Rel Error=0.65%

**Which to Use**:
- **Absolute Error**: When exact capacitance matters (e.g., precision circuits)
- **Relative Error**: When percentage deviation matters (most common in practice)

---

### Common Error Messages

| Message | Cause | Solution |
|---------|-------|----------|
| `Invalid format '5pf' — use '5pF' with capital F` | Lowercase unit suffix | Use capital F: `5pF` |
| `Capacitance cannot be negative. Enter positive value` | Negative value entered | Enter positive value |
| `Cannot parse 'abc'. Expected formats: ...` | Invalid input string | Use supported format (see examples) |
| `N>8 may be slow; consider Heuristic method` | Too many capacitors for SP | Reduce inventory or use Heuristic |
| `No solutions within ±5% tolerance` | All solutions exceed tolerance | Adjust tolerance or add more capacitors |
| `No path between A and B` | Disconnected network (graph method) | Regenerate with different seed or adjust parameters |

---

## Example Workflow

**Goal**: Find a network to achieve 3.1pF using available capacitors.

### Inputs

- **Target**: `3.1pF`
- **Inventory**: `1pF, 2pF, 5pF`
- **Method**: SP Exhaustive
- **Tolerance**: ±5%

### Steps

1. Enter `3.1pF` in target field
2. Add capacitors to inventory:
   - Add row: `1pF`
   - Add row: `2pF`
   - Add row: `5pF`
3. Select "SP Exhaustive" method
4. Set tolerance to `5`
5. Click "Find Solutions"

### Results

Top 3 solutions (example):

| Topology | C_eq | Abs Error | Rel Error | Tolerance |
|----------|------|-----------|-----------|-----------|
| `((C1\|\|C2)+C3)` | `3.0pF` | `0.1pF` | `3.23%` | ✓ |
| `(C1+(C2\|\|C3))` | `3.29pF` | `0.19pF` | `6.13%` | ✗ |
| `(C1\|\|C2\|\|C3)` | `8.0pF` | `4.9pF` | `158%` | ✗ |

**Best Solution**: `((C1||C2)+C3)` with 3.23% error (within ±5% tolerance)

---

## Educational Theory

### View Theory Explanations

Expand the **"Theory"** sections in the app to see:

**SP Enumeration**:
- Algorithm explanation
- Key formulas (parallel: C_p = Σ C_i, series: 1/C_s = Σ (1/C_i))
- When to use this method
- Computational complexity

**Laplacian Graph Method**:
- Nodal analysis approach (Y = s·C, solving with V_a=1, V_b=0)
- Matrix formulation
- Handling singular matrices and disconnected networks
- When to use this method

**Method Comparison**:
- Strengths and limitations of each approach
- Speed vs. accuracy trade-offs
- Topology coverage (SP vs. general graphs)

---

## Advanced Features

### Preset Capacitor Series

Click preset buttons to load standard E-series values:

- **E12**: 12 values per decade (10% tolerance)
- **E24**: 24 values per decade (5% tolerance)
- **E48**: 48 values per decade (2% tolerance)
- **E96**: 96 values per decade (1% tolerance)

**Use Case**: Quickly populate inventory with industry-standard values.

---

### Deterministic Heuristic Search

Set **Random Seed** to the same value (e.g., 42) across multiple runs to get identical results.

**Use Cases**:
- Debugging
- Reproducible research
- Comparing different parameters with same random graphs

---

## Troubleshooting

### App is Slow

**Causes**:
- Too many capacitors in SP exhaustive (N>8)
- Too many iterations in heuristic search
- Large number of internal nodes in heuristic search

**Solutions**:
- Reduce inventory size
- Use heuristic method instead of SP exhaustive
- Reduce iterations (try 1000 instead of 2000)
- Reduce max internal nodes (try 1 instead of 2)

---

### No Solutions Within Tolerance

**Cause**: Available capacitors cannot achieve target within specified tolerance.

**Solutions**:
- Increase tolerance (e.g., from ±5% to ±10%)
- Add more capacitors to inventory
- Adjust target to achievable value
- Use heuristic search with more iterations

---

### Results Look Wrong

**Verification**:
1. Check theory sections to understand formulas
2. Verify results manually for simple cases (e.g., 2 capacitors in series/parallel)
3. Compare SP exhaustive vs. heuristic results for same inputs

**Report Issues**:
- If you find incorrect calculations, please report with:
  - Input parameters (target, inventory, method)
  - Expected vs. actual result
  - Topology expression

---

## Performance Expectations

| Scenario | Expected Time | Notes |
|----------|---------------|-------|
| SP exhaustive, N=5 | <1 second | Fast, instant feedback |
| SP exhaustive, N=8 | ~3 seconds | Acceptable with progress bar |
| Heuristic, 2000 iters, 2 nodes | ~5-10 seconds | Dominated by matrix solves |
| Heuristic, 5000 iters, 3 nodes | ~20-30 seconds | Use for thorough exploration |

**Note**: Times are approximate and depend on hardware.

---

## Next Steps

- **Explore different methods**: Compare SP exhaustive vs. heuristic results
- **Experiment with parameters**: Adjust iterations and internal nodes in heuristic search
- **Read theory sections**: Understand the algorithms behind the magic
- **Export results** (future): Save solutions to file for documentation

---

## Support

- **Documentation**: See project README.md
- **Issues**: Report bugs at [GitHub Issues](https://github.com/yourusername/CapAssigner/issues)
- **Contributions**: Pull requests welcome!

---

**Happy capacitor network design! 🎯⚡**

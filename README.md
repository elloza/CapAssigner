# 🔌 CapAssigner

**Capacitor Network Synthesis Tool**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/elloza/CapAssigner/blob/main/CapAssigner_Colab.ipynb)

CapAssigner is a web-based tool for designing capacitor networks that achieve a target equivalent capacitance. It uses advanced algorithms to explore series-parallel and graph topologies, helping engineers and students find optimal component combinations.

## Features

- **🔬 Series-Parallel Synthesis**: Exhaustive enumeration of all SP topologies (optimal for N ≤ 8 capacitors)
- **�️ SP Graph Exhaustive**: Graph-based enumeration handling internal nodes (N ≤ 6)
- **�📊 Graph Network Search**: Heuristic exploration of non-SP topologies (bridges, meshes)
- **🧮 Laplacian Analysis**: Uses nodal admittance matrices for accurate C_eq calculation
- **📈 Multiple Input Formats**: Accepts values with units (pF, nF, µF), scientific notation (1e-12), and decimals
- **🎓 Educational Content**: Theory explanations with LaTeX formulas for each method
- **📋 E-Series Presets**: Quick loading of standard E12/E24/E48/E96 capacitor values
- **📉 Tolerance Checking**: Visual indicators for solutions meeting tolerance requirements

## Installation

### Prerequisites

- Python 3.7.4 or higher
- Conda (recommended) or pip

### Option 1: Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/CapAssigner.git
cd CapAssigner

# Create and activate environment
conda env create -f environment.yml
conda activate capassigner

# Run the application
streamlit run app.py
```

### Option 2: Pip

```bash
# Clone the repository
git clone https://github.com/yourusername/CapAssigner.git
cd CapAssigner

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Usage

1. **Enter Target Capacitance**: Specify the desired equivalent capacitance (e.g., `3.1pF`)
2. **Set Tolerance**: Define acceptable error percentage (default ±5%)
3. **Add Capacitors**: Enter available capacitor values or load E-series presets
4. **Select Method**:
   - **SP Tree Exhaustive**: For guaranteed optimal SP solutions (N ≤ 8)
   - **SP Graph Exhaustive**: For explicit graph enumeration (N ≤ 6)
   - **Heuristic Graph Search**: For exploring non-SP topologies or larger inventories
5. **Find Solutions**: Click to compute and rank solutions by error
6. **View Results**: Examine circuit diagrams, errors, and tolerance status

### Input Format Examples

| Format | Example | Interpreted Value |
|--------|---------|-------------------|
| With unit | `5.2pF` | 5.2 × 10⁻¹² F |
| Scientific | `1e-12` | 1 × 10⁻¹² F |
| Decimal | `0.0000000000052` | 5.2 × 10⁻¹² F |
| Alternative | `5.2*10^-12` | 5.2 × 10⁻¹² F |

## Architecture

```
capassigner/
├── core/               # Pure Python algorithms (no Streamlit)
│   ├── sp_structures.py   # SP tree dataclasses
│   ├── sp_enumeration.py  # Exhaustive SP enumeration
│   ├── graphs.py          # Graph topology and Laplacian
│   ├── heuristics.py      # Random graph search
│   ├── metrics.py         # Error calculation
│   └── parsing.py         # Input parsing
├── ui/                 # Streamlit UI components
│   ├── pages.py           # Main page layout
│   ├── plots.py           # Circuit diagrams (SchemDraw, NetworkX)
│   ├── theory.py          # Educational content
│   └── tooltips.py        # Help text
└── config.py           # Configuration constants
```

## Algorithms

### Series-Parallel (SP) Enumeration

Generates all possible binary trees combining capacitors with series and parallel operations.

**Formulas:**
- Series: $C_s = \frac{1}{\frac{1}{C_1} + \frac{1}{C_2}}$
- Parallel: $C_p = C_1 + C_2$

**Complexity:** O(Cat(n) × n!) where Cat(n) is the Catalan number

**✅ Strengths:**
- Exhaustive within SP space (finds all possible SP topologies)
- Guaranteed optimal for circuits that ARE pure series-parallel
- Efficient for small N (N ≤ 8 capacitors)
- Well-understood mathematical properties

**⚠️ Limitations:**
- Cannot generate topologies with **internal nodes** (beyond terminals A, B)
- Cannot **reuse capacitor values** on multiple edges
- Cannot represent **bridge circuits** (e.g., Wheatstone bridges)
- Cannot handle **delta-wye** configurations
- Exponential growth makes N > 8 impractical

**Use when:**
- N ≤ 8 capacitors
- Circuit is expected to be pure series-parallel (ladders, standard filters)
- You need guaranteed optimality within SP space

### SP Graph Exhaustive

Enumerates all connected multigraphs with N edges and checks for SP-reducibility.

**Method:**
1. Generate all connected multigraphs with N edges
2. Assign capacitors to edges
3. Check if graph is SP-reducible using iterative reduction
4. Calculate C_eq

**✅ Strengths:**
- Finds **all** SP-reducible topologies, including those with **internal nodes**
- Solves the "Classroom Problem" (bridge-like structures that reduce to SP)
- Guaranteed optimal for any SP-reducible circuit
- Handles capacitor reuse (same value on multiple edges)

**⚠️ Limitations:**
- **Very slow** for N > 6 (super-exponential growth)
- Only finds SP-reducible graphs (no non-SP bridges)

**Use when:**
- N ≤ 6 capacitors
- You suspect the solution requires internal nodes (bridges)
- SP Tree method fails to find an exact solution

### Laplacian Graph Method

Uses nodal admittance matrices to compute C_eq for arbitrary graph topologies.

**Method:**
1. Build Laplacian matrix $\mathbf{Y} = s \cdot \mathbf{C}$
2. Apply boundary conditions: $V_A = 1$, $V_B = 0$
3. Solve for node voltages
4. Calculate $C_{eq} = I_A$

**✅ Strengths:**
- Most general method — handles ANY topology
- Exact calculation using matrix methods (LU decomposition)
- Supports internal nodes (unlimited)
- Handles bridge circuits, meshes, delta-wye configurations
- Fast evaluation O(n³) for single topology

**⚠️ Limitations:**
- Requires explicit topology — cannot enumerate all possibilities
- Not suitable for topology search (too slow to enumerate all graphs)
- User must manually specify graph structure (nodes and edges)

**Use when:**
- You have a specific topology to analyze
- Topology includes internal nodes or bridge structures
- Verifying circuits from textbooks or datasheets

### Heuristic Random Search

Randomly generates graph topologies and evaluates them using Laplacian analysis.

**✅ Strengths:**
- Explores both SP and non-SP topologies
- Can discover unexpected solutions
- Scalable to large N (N > 8 capacitors)
- Configurable iteration count (trade time for quality)
- Reproducible with seed parameter

**⚠️ Limitations:**
- Probabilistic — no guarantee of finding optimal solution
- May miss rare optimal topologies
- Requires many iterations for high-quality results (10,000+)
- Slower than SP enumeration for small N where SP works

**Use when:**
- N > 8 capacitors (SP too slow)
- SP enumeration gives poor results (error > 5%)
- You suspect a non-SP solution exists
- Discovery mode — finding unexpected topologies

## Algorithm Selection Guide

### Decision Flowchart

```
START: Need to find C_eq for capacitor network
  |
  ├─ Do you have a specific topology in mind?
  |    |
  |    ├─ YES → Does it have internal nodes or bridges?
  |    |         |
  |    |         ├─ YES → Use Laplacian Graph Method
  |    |         └─ NO  → Use SP Enumeration
  |    |
  |    └─ NO  → Need to search for topology
  |              |
  |              ├─ N ≤ 8 capacitors?
  |              |    |
  |              |    ├─ YES → Try SP Enumeration first
  |              |    |         |
  |              |    |         ├─ Result error < 1%? → DONE ✅
  |              |    |         └─ Result error > 5%? → Try Heuristic Search
  |              |    |
  |              |    └─ NO  → N > 8, use Heuristic Search
```

### When SP Enumeration Shows High Error (> 5%)

If SP enumeration produces an error greater than 5%, this is a **strong indicator** that:
1. Your problem may require a **non-SP topology** (bridge, mesh, internal nodes)
2. The optimal solution cannot be represented as a pure series-parallel tree
3. You should try **Heuristic Search** with `internal_nodes` enabled

**Example:** The classroom 4-capacitor problem (C₁=2pF, C₂=3pF, C₃=3pF, C₄=1pF, target=1.0pF) produces 7.69% error with SP enumeration because the correct topology requires internal nodes and reusing the 3pF value multiple times — which SP cannot represent.

📚 **See [SP Algorithm Limitations](specs/003-unit-test-suite/SP_ALGORITHM_LIMITATIONS.md) for detailed technical analysis.**

## Comparison Table

| Feature | SP Enumeration | Laplacian Graph | Heuristic Search |
|---------|----------------|-----------------|------------------|
| **Speed** | Slow for N>8 | Very fast (single eval) | Configurable |
| **Topology Coverage** | SP only | All (with explicit spec) | All (random exploration) |
| **Optimality** | Guaranteed (within SP) | Exact (for given topology) | Probabilistic |
| **Internal Nodes** | ❌ No | ✅ Yes | ✅ Yes |
| **Bridge Circuits** | ❌ No | ✅ Yes | ✅ Yes |
| **Best For** | Small N, standard circuits | Verifying specific design | Large N, discovery mode |
| **Time Complexity** | O(Cat(n)×n!) | O(n³) | O(iterations×n³) |

## Testing

CapAssigner includes a comprehensive test suite with 300+ tests covering all core algorithms.

### Running Tests

```bash
# Run all tests (fast: ~6 seconds)
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=capassigner.core --cov-report=term-missing

# Run specific test categories using markers
pytest tests/ -m "unit"         # Unit tests only
pytest tests/ -m "integration"  # Integration tests only
pytest tests/ -m "P1"           # Priority 1 (critical) tests
pytest tests/ -m "fast"         # Fast tests (<1s each)
```

### Test Structure

```
tests/
├── unit/                      # Isolated component tests
│   ├── test_sp_structures.py  # Series/Parallel formula tests
│   ├── test_sp_enumeration.py # Topology enumeration tests
│   ├── test_graphs.py         # Laplacian matrix tests
│   ├── test_heuristics.py     # Random search tests
│   ├── test_metrics.py        # Error calculation tests
│   ├── test_parsing.py        # Input parsing tests
│   └── test_regression.py     # 20+ regression cases
├── integration/               # End-to-end workflow tests
│   └── test_workflows.py      # Full pipeline tests
└── contract/                  # API stability tests
    └── test_algorithm_contracts.py
```

### Test Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Isolated component tests |
| `@pytest.mark.integration` | Cross-module workflow tests |
| `@pytest.mark.P1` | Priority 1 (critical path) |
| `@pytest.mark.P2` | Priority 2 (regression) |
| `@pytest.mark.fast` | Runs in < 1 second |
| `@pytest.mark.slow` | Runs in > 2 seconds |

### Coverage

The test suite achieves **93%+ coverage** of all core modules:
- `metrics.py`: 100%
- `sp_structures.py`: 99%
- `heuristics.py`: 96%
- `parsing.py`: 92%
- `sp_enumeration.py`: 88%
- `graphs.py`: 87%

### Tolerance Levels

Tests use two tolerance levels for floating-point comparisons:
- **EXACT** (`1e-10`): For mathematically exact solutions (e.g., series of equal caps)
- **APPROXIMATE** (`1e-6`): For numerical approximations (0.1% relative error)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

*Built with ❤️ using Streamlit, NetworkX, SchemDraw, and NumPy*
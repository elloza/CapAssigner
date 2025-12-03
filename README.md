# 🔌 CapAssigner

**Capacitor Network Synthesis Tool**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/elloza/CapAssigner/blob/main/CapAssigner_Colab.ipynb)

CapAssigner is a web-based tool for designing capacitor networks that achieve a target equivalent capacitance. It uses advanced algorithms to explore series-parallel and graph topologies, helping engineers and students find optimal component combinations.

## Features

- **🔬 Series-Parallel Synthesis**: Exhaustive enumeration of all SP topologies (optimal for N ≤ 8 capacitors)
- **📊 Graph Network Search**: Heuristic exploration of non-SP topologies (bridges, meshes)
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
   - **SP Exhaustive**: For guaranteed optimal solutions with N ≤ 8 components
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

### Series-Parallel Enumeration

Generates all possible binary trees combining capacitors with series and parallel operations.

**Formulas:**
- Series: $C_s = \frac{1}{\frac{1}{C_1} + \frac{1}{C_2}}$
- Parallel: $C_p = C_1 + C_2$

**Complexity:** O(Cat(n) × n!) where Cat(n) is the Catalan number

### Laplacian Graph Method

Uses nodal admittance matrices to compute C_eq for arbitrary graph topologies.

**Method:**
1. Build Laplacian matrix $\mathbf{Y} = s \cdot \mathbf{C}$
2. Apply boundary conditions: $V_A = 1$, $V_B = 0$
3. Solve for node voltages
4. Calculate $C_{eq} = I_A$

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/unit/test_sp_structures.py -v
pytest tests/unit/test_graphs.py -v
pytest tests/unit/test_heuristics.py -v
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

*Built with ❤️ using Streamlit, NetworkX, SchemDraw, and NumPy*
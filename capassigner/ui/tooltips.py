"""Centralized tooltip text for UI widgets.

This module contains all help text (tooltips) for Streamlit widgets,
ensuring consistency and easy maintenance of user-facing documentation.

Constitutional Compliance:
    - Principle II (UX First): Clear, helpful tooltip text
    - Principle III (Robust Input): Input format examples and constraints
"""

# Capacitor input tooltips
TOOLTIP_CAP_LIST = """
**Enter capacitor values, one per line or comma-separated.**

**Supported formats:**
- With units: `1pF`, `2.2nF`, `100µF`, `0.1mF`, `1F`
- Scientific notation: `1e-12`, `2.2e-9`, `1.5*10^-6`
- Plain numbers (interpreted as Farads): `0.000000000001`

**Examples:**
```
1pF
2.2pF, 4.7pF
1e-12
100nF
```
"""

TOOLTIP_CAP_TARGET = """
**Target equivalent capacitance to achieve.**

**Supported formats:**
- With units: `5.2pF`, `0.1µF`, `100nF`
- Scientific notation: `1e-11`, `5.2*10^-12`
- Plain numbers (Farads): `0.0000000000052`

**Examples:** `5.2pF`, `0.1µF`, `1e-11`

The synthesis algorithm will find capacitor networks
with equivalent capacitance as close as possible to this target.
"""

TOOLTIP_TOLERANCE = """
**Acceptable error percentage (±).**

Solutions with relative error ≤ tolerance will be marked as "within tolerance".

- Default: 1%
- Example: 5% means solutions within ±5% of target are acceptable

**Note:** This does not filter results, only marks which solutions meet the tolerance.
"""

# Method selection tooltips
TOOLTIP_METHOD_SIMPLE = """
**Fast two-level series-parallel combinations.**

Quick approximations suitable for any number of capacitors.
Limited to simple topologies.
"""

TOOLTIP_METHOD_SP_TREE = """
**SP Tree Exhaustive - Series-Parallel Enumeration**

Exhaustively enumerates ALL possible series-parallel binary trees.

- ✅ **Guaranteed optimal** within SP tree space
- ⚠️ **Slow for N > 8** (Catalan × N! complexity)
- ⚠️ **Cannot find internal nodes** (pure series/parallel only)
- 📐 Topologies: Binary trees with series/parallel operations
"""

TOOLTIP_METHOD_SP_GRAPH = """
**SP Graph Exhaustive - Graph Enumeration**

Enumerates all connected multigraphs and checks for SP-reducibility.

- ✅ **Finds internal nodes** (bridges that reduce to SP)
- ✅ **Solves Classroom Problem** (e.g., [3,2,3,1] -> 1)
- ⚠️ **Very Slow for N > 6** (Super-exponential)
- 📐 Topologies: General graphs that are SP-reducible
"""

TOOLTIP_METHOD_HEURISTIC = """
**Heuristic Graph Search - Random Exploration**

Randomly generates graph topologies including non-SP networks
(bridges, meshes, delta/wye configurations).

- ✅ Handles **N > 8** efficiently
- ✅ Discovers **non-SP solutions**
- ⚠️ **No optimality guarantee** (probabilistic)
- 🎲 **Deterministic** with seed parameter
"""

TOOLTIP_MAX_N_SP = """
**Maximum capacitors for SP Exhaustive enumeration.**

Higher values dramatically increase computation time.
- N=6: ~5,040 topologies (fast)
- N=7: ~35,280 topologies (moderate)
- N=8: ~264,600 topologies (slow)
- N>8: Not recommended (use Heuristic instead)

**Constitutional default:** 8
"""

# Heuristic parameters
TOOLTIP_HEURISTIC_ITERS = """
**Number of random graph topologies to explore.**

More iterations = higher probability of finding optimal solution.

- **100-500**: Quick exploration
- **1000-2000**: Balanced (default)
- **5000-10000**: Thorough search

**Trade-off:** More iterations = longer execution time.
**Constitutional default:** 2000
"""

TOOLTIP_HEURISTIC_INTERNAL = """
**Maximum internal nodes (besides terminals A and B).**

Internal nodes allow more complex topologies:
- **0**: Direct connections only (simple graphs)
- **1**: Allows Y/Delta structures
- **2**: Enables complex bridges (default)
- **3+**: Very complex topologies

**Trade-off:** More nodes = larger search space.
**Constitutional default:** 2
"""

TOOLTIP_SEED = """
**Random seed for reproducible results.**

Using the same seed with identical inputs produces identical results.

- **0**: Use default seed
- **Any positive integer**: Custom seed for reproducibility

**Use case:** Set a seed to share and reproduce exact results.
**Constitutional default:** 0
"""

# UI appearance
TOOLTIP_UI_SCALE = """
**Global UI scaling factor.**

Adjusts text size and widget dimensions.
"""

TOOLTIP_DIAGRAM_SCALE = """
**Scaling factor for circuit diagrams and graphs.**

Larger values = bigger visualizations.
"""

# Results tooltips
TOOLTIP_RESULTS_CEQ = """
**Equivalent capacitance of the network topology.**

Calculated using:
- **SP topologies**: Series/parallel formulas
- **Graph topologies**: Laplacian nodal analysis
"""

TOOLTIP_RESULTS_ERROR = """
**Absolute error = |C_eq - C_target|**

The difference between achieved and target capacitance.
"""

TOOLTIP_RESULTS_REL_ERROR = """
**Relative error = |C_eq - C_target| / C_target × 100%**

Percentage deviation from target. Lower is better.
"""


TOOLTIP_METHOD_SELECTOR = """
**Select the synthesis algorithm.**

- **SP Tree Exhaustive**: Fast, exact for standard series-parallel circuits. Best for N <= 8.
- **SP Graph Exhaustive**: Exact for all SP-reducible circuits, including those with internal nodes (bridges). Slower, best for N <= 6.
- **Heuristic Graph Search**: Approximate, finds non-SP solutions (bridges). Best for N > 8 or complex targets.
"""


def get_tooltip(key: str) -> str:
    """Retrieve tooltip text by key.

    Args:
        key: Tooltip identifier (e.g., 'CAP_LIST', 'METHOD_SP').
             The 'TOOLTIP_' prefix is optional.

    Returns:
        Tooltip text string, or empty string if key not found.

    Example:
        >>> get_tooltip('CAP_TARGET')
        'Target equivalent capacitance. Accepts same formats...'
        >>> get_tooltip('TOOLTIP_CAP_TARGET')
        'Target equivalent capacitance. Accepts same formats...'
    """
    # Handle both with and without prefix
    if not key.startswith("TOOLTIP_"):
        key = f"TOOLTIP_{key}"
    
    return globals().get(key, "")

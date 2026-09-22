# Data Model: Lcapy Circuit Visualization

**Feature ID**: `006-lcapy-visualization`  
**Phase**: Design  
**Date**: 2025-12-12

---

## Overview

This document defines the data structures and formats used for converting CapAssigner circuit representations (SPNode and GraphTopology) into lcapy netlist format for professional circuit visualization.

---

## Entity 1: Netlist String

**Purpose**: SPICE-format netlist string that lcapy can parse to generate circuit diagrams

### Structure

```python
netlist: str  # Multi-line string with component definitions
```

### Format

```
<component_name> <node1> <node2> <value><unit>
<component_name> <node1> <node2> <value><unit>
...
```

### Rules

1. **Component Names**: 
   - Must start with `C` (capacitor)
   - Followed by unique identifier (e.g., `C1`, `C2`, `C_A_B`)
   - No spaces allowed

2. **Node Numbers**:
   - Terminal A: Always node `1`
   - Terminal B: Always node `0` (ground reference)
   - Internal nodes: `2`, `3`, `4`, ... (sequential)
   - Nodes must be integers or simple strings

3. **Values**:
   - Numeric value followed immediately by unit
   - Units: `F`, `mF`, `uF` (not µF), `nF`, `pF`
   - Use appropriate SI prefix for readability
   - 6 significant figures maximum

4. **Whitespace**:
   - Single space between fields
   - Newline (`\n`) between component definitions
   - No leading/trailing whitespace

### Examples

**Simple Series**:
```
C1 1 2 10uF
C2 2 0 5uF
```

**Simple Parallel**:
```
C1 1 0 10uF
C2 1 0 5uF
```

**Complex (Series-Parallel)**:
```
C1 1 2 15uF
C2 2 3 3uF
C3 3 0 6uF
C4 1 0 20uF
```

### Validation Rules

1. At least one component must be defined
2. Node 0 must be reachable from node 1 (connected circuit)
3. All node numbers must be non-negative integers
4. All values must be positive real numbers
5. Component names must be unique

---

## Entity 2: SPNode Conversion Metadata

**Purpose**: Track node assignments during SPNode → netlist conversion

### Structure

```python
@dataclass
class SPConversionContext:
    """Context for converting SPNode tree to netlist."""
    
    next_node: int              # Next available node number (starts at 2)
    netlist_lines: List[str]    # Accumulated netlist component definitions
    capacitors: List[float]     # Capacitor values in Farads
    labels: List[str]           # Capacitor labels (C1, C2, ...)
```

### Node Numbering Strategy

```
Terminal A → Node 1 (input)
Terminal B → Node 0 (ground/output)
Internal nodes → 2, 3, 4, ... (sequential allocation)
```

### Conversion Rules

**Leaf Node**:
```python
Leaf(index=i, value=v) → "{label[i]} {in_node} {out_node} {format(capacitors[i])}"
```

**Series Node**:
```python
Series(left, right):
  1. Allocate mid_node = next_node++
  2. Convert left: in_node → mid_node
  3. Convert right: mid_node → out_node
```

**Parallel Node**:
```python
Parallel(left, right):
  1. Convert left: in_node → out_node
  2. Convert right: in_node → out_node
  (Both branches connect same nodes)
```

### Example

**Input**: `Series(Leaf(0), Parallel(Leaf(1), Leaf(2)))`  
**Capacitors**: `[10e-6, 5e-6, 5e-6]` Farads  
**Labels**: `["C1", "C2", "C3"]`

**Conversion Process**:
1. Series: Allocate mid_node = 2
2. Convert Leaf(0): C1 from node 1 to node 2
3. Parallel: Both connect node 2 to node 0
4. Convert Leaf(1): C2 from node 2 to node 0
5. Convert Leaf(2): C3 from node 2 to node 0

**Output Netlist**:
```
C1 1 2 10uF
C2 2 0 5uF
C3 2 0 5uF
```

---

## Entity 3: Graph Topology Conversion Metadata

**Purpose**: Map NetworkX graph nodes to lcapy netlist nodes

### Structure

```python
@dataclass
class GraphConversionContext:
    """Context for converting GraphTopology to netlist."""
    
    node_map: Dict[Any, int]     # Graph node → netlist node number
    edge_labels: Dict[Tuple[Any, Any], int]  # Track parallel edge count
    netlist_lines: List[str]     # Accumulated netlist lines
```

### Node Mapping Strategy

```python
node_map = {
    terminal_a: 1,              # Terminal A always node 1
    terminal_b: 0,              # Terminal B always node 0 (ground)
    internal_nodes[0]: 2,       # First internal node
    internal_nodes[1]: 3,       # Second internal node
    ...
}
```

### Edge Labeling Strategy

For MultiGraph support (parallel edges between same nodes):

```python
edge_count[(u, v)] = number of edges already processed between u and v

If edge_count == 0:
    label = f"C{u}{v}"         # First edge: simple label
Else:
    label = f"C{u}{v}_{edge_count}"  # Subsequent edges: add counter
```

### Example

**Input**: GraphTopology with 3 nodes, 4 edges
- Nodes: `['A', 'B', '2']` (A=terminal_a, B=terminal_b, '2'=internal)
- Edges: 
  - A → '2': 8µF
  - '2' → B: 7µF  
  - A → B: 2µF
  - A → B: 4µF (parallel edge)

**Node Mapping**:
```python
{
    'A': 1,
    'B': 0,
    '2': 2
}
```

**Edge Processing**:
1. A → '2' (8µF): `CA2 1 2 8uF`
2. '2' → B (7µF): `C2B 2 0 7uF`
3. A → B (2µF): `CAB 1 0 2uF` (first A-B edge)
4. A → B (4µF): `CAB_1 1 0 4uF` (second A-B edge, add counter)

**Output Netlist**:
```
CA2 1 2 8uF
C2B 2 0 7uF
CAB 1 0 2uF
CAB_1 1 0 4uF
```

---

## Entity 4: Capacitance Value Formatting

**Purpose**: Convert Farad values to human-readable netlist format

### Format Rules

| Magnitude Range | Unit | Example Input (F) | Example Output |
|----------------|------|-------------------|----------------|
| ≥ 1×10⁻³ | `mF` | 0.002 | `2mF` |
| ≥ 1×10⁻⁶ | `uF` | 1.5×10⁻⁵ | `15uF` |
| ≥ 1×10⁻⁹ | `nF` | 5×10⁻⁹ | `5nF` |
| ≥ 1×10⁻¹² | `pF` | 3.3×10⁻¹² | `3.3pF` |
| < 1×10⁻¹² | `F` | 1×10⁻¹⁵ | `0.001pF` or `1e-15F` |

### Algorithm

```python
def format_for_netlist(value_farads: float) -> str:
    """Format capacitance for lcapy netlist."""
    abs_val = abs(value_farads)
    
    if abs_val >= 1e-3:
        return f"{value_farads * 1e3:.6g}mF"
    elif abs_val >= 1e-6:
        return f"{value_farads * 1e6:.6g}uF"  # Note: 'u' not 'µ'
    elif abs_val >= 1e-9:
        return f"{value_farads * 1e9:.6g}nF"
    elif abs_val >= 1e-12:
        return f"{value_farads * 1e12:.6g}pF"
    else:
        return f"{value_farads:.6g}F"  # Fallback
```

### Key Points

- Use `u` not `µ` (lcapy requirement)
- Use `.6g` format (6 significant figures, removes trailing zeros)
- Always positive values (capacitance cannot be negative)
- No spaces between number and unit

---

## Entity 5: Rendering Configuration

**Purpose**: Configuration parameters for lcapy drawing

### Structure

```python
@dataclass
class LcapyRenderConfig:
    """Configuration for lcapy circuit rendering."""
    
    # Node display
    draw_nodes: str = 'none'         # 'none', 'primary', 'connections', 'all'
    label_nodes: bool = False        # Show node numbers
    
    # Component display
    label_ids: bool = False          # Show component IDs (C1, C2)
    label_values: bool = True        # Show capacitance values
    
    # Style
    style: str = 'american'          # 'american' or 'european'
    node_spacing: float = 2.0        # Space between components
    cpt_size: float = 1.5            # Component size multiplier
    
    # Output
    dpi: int = 150                   # Resolution (dots per inch)
    scale: float = 1.0               # Overall scale factor
```

### Recommended Defaults

For CapAssigner application:
- `draw_nodes='none'`: Cleaner appearance
- `label_values=True`: Users need to see values
- `style='american'`: Standard in US engineering
- `dpi=150`: Good screen quality without excessive size

### Usage

```python
config = LcapyRenderConfig()
fig = circuit.draw(**asdict(config))
```

---

## Data Flow Diagram

```
[SPNode Tree]
     |
     | sp_to_netlist()
     ↓
[Netlist String]
     |
     | Circuit(netlist)
     ↓
[Lcapy Circuit]
     |
     | circuit.draw(**config)
     ↓
[Matplotlib Figure]
```

```
[GraphTopology (NetworkX)]
     |
     | graph_to_netlist()
     ↓
[Netlist String]
     |
     | Circuit(netlist)
     ↓
[Lcapy Circuit]
     |
     | circuit.draw(**config)
     ↓
[Matplotlib Figure]
```

---

## Validation Requirements

### Netlist Validation

Before passing to lcapy:
1. ✅ All component names unique
2. ✅ All node references valid (integers ≥ 0)
3. ✅ All values positive real numbers
4. ✅ Circuit is connected (path exists from node 1 to node 0)
5. ✅ At least one component defined

### Conversion Validation

After conversion:
1. ✅ Number of netlist components matches input capacitor count
2. ✅ All capacitor labels appear exactly once
3. ✅ Node numbering sequential (no gaps: 1, 0, 2, 3, ...)

### Rendering Validation

After rendering:
1. ✅ Matplotlib Figure object returned
2. ✅ Figure has axes with circuit elements
3. ✅ No exceptions raised during draw()

---

## Error Handling

### Invalid Netlist

**Error**: Lcapy parsing fails  
**Cause**: Malformed netlist syntax  
**Handling**: Log error, fallback to old rendering

### Empty Circuit

**Error**: No components in netlist  
**Cause**: Empty SPNode or GraphTopology  
**Handling**: Raise ValueError with clear message

### Node Disconnected

**Error**: Circuit not connected between terminals  
**Cause**: Bug in conversion algorithm  
**Handling**: Log warning, attempt render anyway (lcapy may handle)

---

## Examples

### Example 1: Simple Series

**SPNode**:
```python
Series(Leaf(0, 10e-6), Leaf(1, 5e-6))
```

**Netlist**:
```
C1 1 2 10uF
C2 2 0 5uF
```

### Example 2: Simple Parallel

**SPNode**:
```python
Parallel(Leaf(0, 10e-6), Leaf(1, 5e-6))
```

**Netlist**:
```
C1 1 0 10uF
C2 1 0 5uF
```

### Example 3: Exercise 02 (Complex Graph)

**GraphTopology**:
- 3 nodes: A(terminal), B(terminal), 2(internal)
- 4 edges: 8µF, 7µF, 2µF, 4µF

**Netlist**:
```
CA2 1 2 8uF
C2B 2 0 7uF
CAB 1 0 2uF
CAB_1 1 0 4uF
```

---

## References

- **Lcapy Netlist Documentation**: https://lcapy.readthedocs.io/en/latest/netlists.html
- **SPICE Netlist Format**: Standard reference for component syntax
- **CapAssigner SPNode**: `capassigner/core/sp_structures.py`
- **CapAssigner GraphTopology**: `capassigner/core/graphs.py`

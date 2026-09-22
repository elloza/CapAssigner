# Quickstart Guide: Lcapy Circuit Visualization

**Feature ID**: `006-lcapy-visualization`  
**Estimated Time**: 2-3 hours  
**Difficulty**: Moderate

---

## Overview

This guide walks through implementing professional circuit visualization using lcapy. You'll convert SPNode and GraphTopology structures to lcapy netlist format and integrate rendering into the existing application.

---

## Prerequisites

✅ **Before you start:**
- [ ] Lcapy installed (`pip install lcapy`) 
- [ ] Familiar with SPNode structure (Leaf, Series, Parallel)
- [ ] Familiar with GraphTopology and NetworkX graphs
- [ ] Read [spec.md](spec.md), [plan.md](plan.md), and [research.md](research.md)

---

## Step 1: Add Helper Function for Value Formatting (15 min)

**Location**: `capassigner/ui/plots.py`

Add this function after existing `_format_capacitance()`:

```python
def _format_capacitance_for_netlist(value_farads: float) -> str:
    """Format capacitance value for lcapy netlist.
    
    Args:
        value_farads: Capacitance in Farads
        
    Returns:
        Formatted string like "10uF", "3.3nF", etc.
    """
    abs_val = abs(value_farads)
    
    if abs_val >= 1e-3:  # >= 1mF
        return f"{value_farads * 1e3:.6g}mF"
    elif abs_val >= 1e-6:  # >= 1µF
        return f"{value_farads * 1e6:.6g}uF"  # Use 'u' not 'µ'
    elif abs_val >= 1e-9:  # >= 1nF
        return f"{value_farads * 1e9:.6g}nF"
    elif abs_val >= 1e-12:  # >= 1pF
        return f"{value_farads * 1e12:.6g}pF"
    else:
        return f"{value_farads:.6g}F"
```

**Test it**:
```python
# In Python console or test file
assert _format_capacitance_for_netlist(1.5e-05) == "15uF"
assert _format_capacitance_for_netlist(3.3e-09) == "3.3nF"
```

---

## Step 2: Implement SPNode to Netlist Conversion (30 min)

**Location**: `capassigner/ui/plots.py`

Add these functions:

```python
def _sp_to_lcapy_netlist(
    node: SPNode,
    in_node: int,
    out_node: int,
    capacitors: List[float],
    labels: List[str],
    next_node_ref: List[int],
    lines: List[str]
) -> None:
    """
    Recursively convert SPNode to netlist lines.
    
    Args:
        node: Current SPNode
        in_node: Input node number
        out_node: Output node number
        capacitors: Capacitance values in Farads
        labels: Capacitor labels
        next_node_ref: [next_available_node] (mutable)
        lines: Accumulated netlist lines (mutable)
    """
    if isinstance(node, Leaf):
        # Base case: single capacitor
        cap_val = capacitors[node.capacitor_index]
        label = labels[node.capacitor_index]
        val_str = _format_capacitance_for_netlist(cap_val)
        lines.append(f"{label} {in_node} {out_node} {val_str}")
        
    elif isinstance(node, Series):
        # Series: in -> left -> mid -> right -> out
        mid_node = next_node_ref[0]
        next_node_ref[0] += 1
        
        _sp_to_lcapy_netlist(node.left, in_node, mid_node,
                            capacitors, labels, next_node_ref, lines)
        _sp_to_lcapy_netlist(node.right, mid_node, out_node,
                            capacitors, labels, next_node_ref, lines)
        
    elif isinstance(node, Parallel):
        # Parallel: both connect in to out
        _sp_to_lcapy_netlist(node.left, in_node, out_node,
                            capacitors, labels, next_node_ref, lines)
        _sp_to_lcapy_netlist(node.right, in_node, out_node,
                            capacitors, labels, next_node_ref, lines)
    else:
        raise TypeError(f"Unknown SPNode type: {type(node)}")


def sp_to_lcapy_netlist(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: List[float]
) -> str:
    """
    Convert SPNode tree to lcapy netlist format.
    
    Args:
        node: Root SPNode
        capacitor_labels: Labels for capacitors
        capacitor_values: Capacitance values in Farads
        
    Returns:
        Netlist string (multiline)
    """
    lines = []
    next_node_ref = [2]  # Start internal nodes at 2
    
    # Terminal A = node 1, Terminal B = node 0
    _sp_to_lcapy_netlist(node, 1, 0, capacitor_values, 
                        capacitor_labels, next_node_ref, lines)
    
    return "\n".join(lines)
```

**Test it**:
```python
# Series example
node = Series(Leaf(0, 1e-05), Leaf(1, 5e-06))
netlist = sp_to_lcapy_netlist(node, ["C1", "C2"], [1e-05, 5e-06])
# Expected:
# C1 1 2 10uF
# C2 2 0 5uF
```

---

## Step 3: Implement Graph to Netlist Conversion (30 min)

**Location**: `capassigner/ui/plots.py`

Add this function:

```python
def graph_to_lcapy_netlist(
    topology: GraphTopology,
    capacitor_labels: Optional[List[str]] = None
) -> str:
    """
    Convert GraphTopology to lcapy netlist format.
    
    Args:
        topology: GraphTopology with NetworkX graph
        capacitor_labels: Optional custom labels
        
    Returns:
        Netlist string (multiline)
    """
    graph = topology.graph
    
    # Create node mapping
    node_map = {
        topology.terminal_a: 1,
        topology.terminal_b: 0
    }
    next_node = 2
    for internal_node in topology.internal_nodes:
        node_map[internal_node] = next_node
        next_node += 1
    
    # Generate netlist lines
    lines = []
    edge_count = {}
    
    for u, v, key, data in graph.edges(keys=True, data=True):
        cap = data.get('capacitance', 0)
        cap_str = _format_capacitance_for_netlist(cap)
        
        # Generate unique label for edge
        pair = tuple(sorted([u, v]))
        edge_num = edge_count.get(pair, 0)
        edge_count[pair] = edge_num + 1
        
        # Create label
        if edge_num == 0:
            label = f"C{u}{v}"
        else:
            label = f"C{u}{v}_{edge_num}"
        
        # Clean label (remove special chars)
        label = label.replace(" ", "").replace("-", "")
        
        node1 = node_map[u]
        node2 = node_map[v]
        
        lines.append(f"{label} {node1} {node2} {cap_str}")
    
    return "\n".join(lines)
```

**Test it**:
```python
# Simple graph
G = nx.MultiGraph()
G.add_edge('A', 'B', capacitance=1e-05)
topology = GraphTopology(G, 'A', 'B', [])
netlist = graph_to_lcapy_netlist(topology)
# Expected: CAB 1 0 10uF
```

---

## Step 4: Add Lcapy Check at Module Level (5 min)

**Location**: `capassigner/ui/plots.py` (top of file)

After the schemdraw import block, add:

```python
# Check for lcapy availability
try:
    from lcapy import Circuit as LcapyCircuit
    LCAPY_AVAILABLE = True
except ImportError:
    LCAPY_AVAILABLE = False
    LcapyCircuit = None
```

---

## Step 5: Update render_sp_circuit to Use Lcapy (30 min)

**Location**: `capassigner/ui/plots.py`

Replace the existing `render_sp_circuit` function body with:

```python
def render_sp_circuit(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: Optional[List[float]] = None
) -> plt.Figure:
    """Render series-parallel network as circuit diagram.
    
    Tries lcapy first, falls back to schemdraw if unavailable or errors.
    """
    # Try lcapy rendering first
    if LCAPY_AVAILABLE and capacitor_values is not None:
        try:
            netlist = sp_to_lcapy_netlist(node, capacitor_labels, capacitor_values)
            circuit = LcapyCircuit(netlist)
            
            # Draw with professional settings
            fig = circuit.draw(
                draw_nodes='none',
                label_nodes=False,
                label_values=True,
                style='american',
                dpi=150
            )
            
            return fig
            
        except Exception as e:
            import logging
            logging.warning(f"Lcapy rendering failed: {e}, using schemdraw fallback")
    
    # Fallback to existing schemdraw rendering
    if not SCHEMDRAW_AVAILABLE:
        raise ImportError("Neither lcapy nor schemdraw available for rendering")
    
    # ... existing schemdraw code ...
    # (Keep the existing schemdraw implementation as fallback)
```

---

## Step 6: Update render_graph_network to Use Lcapy (30 min)

**Location**: `capassigner/ui/plots.py`

Replace `_render_graph_as_circuit_matplotlib` with lcapy version:

```python
def render_graph_network(
    topology: GraphTopology,
    scale: float = 1.0,
    font_size: int = 10
) -> plt.Figure:
    """Render general graph network as circuit schematic.
    
    Tries lcapy first, falls back to matplotlib if unavailable or errors.
    """
    # Try lcapy rendering first
    if LCAPY_AVAILABLE:
        try:
            netlist = graph_to_lcapy_netlist(topology)
            circuit = LcapyCircuit(netlist)
            
            # Draw with configuration
            fig = circuit.draw(
                draw_nodes='connections',  # Show internal nodes
                label_nodes=True,
                label_values=True,
                style='american',
                dpi=150,
                scale=scale
            )
            
            return fig
            
        except Exception as e:
            import logging
            logging.warning(f"Lcapy graph rendering failed: {e}, using matplotlib fallback")
    
    # Fallback to existing matplotlib rendering
    return _render_graph_as_circuit_matplotlib(topology, scale, font_size)
```

---

## Step 7: Test with Real Circuits (30 min)

**Create test file**: `tests/unit/test_plots_lcapy.py`

```python
import pytest
from capassigner.core.sp_structures import Leaf, Series, Parallel
from capassigner.ui.plots import (
    sp_to_lcapy_netlist,
    render_sp_circuit,
    LCAPY_AVAILABLE
)

@pytest.mark.skipif(not LCAPY_AVAILABLE, reason="lcapy not installed")
class TestLcapyRendering:
    
    def test_single_capacitor_netlist(self):
        node = Leaf(0, 1e-05)
        netlist = sp_to_lcapy_netlist(node, ["C1"], [1e-05])
        assert netlist == "C1 1 0 10uF"
    
    def test_series_netlist(self):
        node = Series(Leaf(0, 1e-05), Leaf(1, 5e-06))
        netlist = sp_to_lcapy_netlist(node, ["C1", "C2"], [1e-05, 5e-06])
        lines = netlist.split("\n")
        assert len(lines) == 2
        assert "C1 1 2 10uF" in lines
        assert "C2 2 0 5uF" in lines
    
    def test_parallel_netlist(self):
        node = Parallel(Leaf(0, 1e-05), Leaf(1, 5e-06))
        netlist = sp_to_lcapy_netlist(node, ["C1", "C2"], [1e-05, 5e-06])
        lines = netlist.split("\n")
        assert len(lines) == 2
        assert "C1 1 0 10uF" in lines
        assert "C2 1 0 5uF" in lines
    
    def test_render_sp_circuit(self):
        node = Series(Leaf(0, 1e-05), Leaf(1, 5e-06))
        fig = render_sp_circuit(node, ["C1", "C2"], [1e-05, 5e-06])
        assert fig is not None
        assert len(fig.axes) > 0
```

**Run tests**:
```bash
.\.conda\python.exe -m pytest tests/unit/test_plots_lcapy.py -v
```

---

## Step 8: Visual Validation (15 min)

Test in Streamlit app:

1. **Start app**: `streamlit run app.py`
2. **Test Case 1**: Enter 2 capacitors (10µF, 5µF), target 3.33µF
3. **Verify**: Circuit diagram shows both capacitors correctly
4. **Test Case 2**: Exercise 02 from PDF (2µF, 8µF, 7µF, 4µF)
5. **Verify**: All 4 capacitors visible in graph diagram

**Checklist**:
- [ ] All capacitors present in diagram
- [ ] Terminal A and B labeled
- [ ] Values displayed correctly
- [ ] Professional appearance
- [ ] No floating wires
- [ ] Renders in < 2 seconds

---

## Step 9: Documentation Updates (10 min)

Update docstrings to mention lcapy:

```python
def render_sp_circuit(...):
    """Render series-parallel network using lcapy (falls back to schemdraw).
    
    Uses lcapy for professional CircuiTikZ-quality diagrams. If lcapy
    is unavailable or rendering fails, falls back to schemdraw.
    ...
    """
```

---

## Common Issues & Solutions

### Issue 1: "Lcapy not found"

**Solution**: Install lcapy
```bash
.\.conda\python.exe -m pip install lcapy
```

### Issue 2: "Invalid netlist syntax"

**Solution**: Check node numbering
- Terminal A must be node 1
- Terminal B must be node 0
- Internal nodes sequential from 2

### Issue 3: "Circuit not connected"

**Solution**: Verify all paths from node 1 reach node 0

### Issue 4: Fallback always triggered

**Solution**: Check `LCAPY_AVAILABLE` flag and import errors
```python
print(f"LCAPY_AVAILABLE: {LCAPY_AVAILABLE}")
```

---

## After Implementation

1. **Run full test suite**: 
   ```bash
   .\.conda\python.exe -m pytest tests/ -v
   ```

2. **Visual regression test**: Compare old vs new diagrams

3. **Performance test**: Ensure < 2s per diagram

4. **Code review**: Check for:
   - Type hints on all functions
   - Docstrings complete
   - Error handling robust
   - Fallback tested

5. **Update IMPLEMENTATION_SUMMARY.md** with results

---

## Success Criteria Checklist

After implementation, verify:

- [ ] **SC-001**: Diagrams look professional and publication-ready
- [ ] **SC-002**: All topologies supported (SP and graph)
- [ ] **SC-003**: No regressions (all tests pass)
- [ ] **SC-004**: Code complexity reduced

- [ ] **US1**: Professional SP circuit diagrams
- [ ] **US2**: Clear graph topology visualization  
- [ ] **US3**: Unified rendering system

---

## Timeline

**Total: 2-3 hours**

- Step 1-2: 45 minutes (SPNode conversion)
- Step 3: 30 minutes (Graph conversion)
- Step 4-6: 1 hour (Integration)
- Step 7-8: 45 minutes (Testing)
- Step 9: 10 minutes (Documentation)

---

## Next Steps After Completion

1. Monitor for edge cases in production
2. Consider removing schemdraw after 2-3 stable releases
3. Optional: Add LaTeX/CircuiTikZ export feature
4. Optional: Add layout customization options

---

## References

- **Research Decisions**: [research.md](research.md)
- **Data Structures**: [data-model.md](data-model.md)
- **API Contracts**: [contracts/lcapy-rendering.yaml](contracts/lcapy-rendering.yaml)
- **Lcapy Docs**: https://lcapy.readthedocs.io/en/latest/

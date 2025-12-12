"""Visualization functions for network topologies.

This module provides plotting functions using lcapy for professional circuit diagrams,
with fallback to SchemDraw for series-parallel circuits and NetworkX for general 
graph topologies.

Constitutional Compliance:
    - Principle II (UX First): Clear visual circuit diagrams
    - Principle IV (Modular Architecture): Pure rendering, no business logic
"""

from __future__ import annotations
import logging
import matplotlib.pyplot as plt
from typing import Any, Dict, List, Tuple, Optional

import networkx as nx

# Check for lcapy availability (professional circuit rendering)
try:
    from lcapy import Circuit as LcapyCircuit
    LCAPY_AVAILABLE = True
except ImportError:
    LCAPY_AVAILABLE = False
    LcapyCircuit = None

# Check for schemdraw availability (fallback rendering)
try:
    import schemdraw
    import schemdraw.elements as elm
    SCHEMDRAW_AVAILABLE = True
except ImportError:
    SCHEMDRAW_AVAILABLE = False

from capassigner.core.sp_structures import Leaf, Series, Parallel, SPNode
from capassigner.core.graphs import GraphTopology

# Logger for rendering warnings and errors
logger = logging.getLogger(__name__)

# Color constants for better visibility
LABEL_COLOR = '#CC0000'  # Red color for capacitor labels
TERMINAL_COLOR = '#CC0000'  # Red for terminal labels


def render_sp_circuit(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: Optional[List[float]] = None
) -> plt.Figure:
    """Render series-parallel network as professional circuit diagram.

    Uses lcapy for professional CircuiTikZ-quality diagrams. If lcapy is
    unavailable or rendering fails, falls back to schemdraw.

    Creates a circuit diagram with labeled components and terminals A-B.
    Recursively traverses SP tree structure to build the circuit.

    Args:
        node: Root SPNode of the network topology.
        capacitor_labels: Labels for capacitors (e.g., ["C1", "C2", "C3"]).
        capacitor_values: Optional list of capacitance values for display.

    Returns:
        Matplotlib figure containing the circuit diagram.

    Raises:
        ImportError: If neither lcapy nor SchemDraw is available.
        TypeError: If node is not a valid SPNode type.

    Examples:
        >>> leaf = Leaf(0, 5e-12)
        >>> fig = render_sp_circuit(leaf, ["C1"], [5e-12])
        >>> # Returns figure with A--[C1=5.0pF]--B
        
    Constitutional Compliance:
        - Principle II (UX First): Professional circuit diagrams
        - Principle IV (Modular Architecture): No Streamlit coupling
    """
    # Try lcapy rendering first (professional quality)
    if LCAPY_AVAILABLE and capacitor_values is not None:
        try:
            netlist = sp_to_lcapy_netlist(node, capacitor_labels, capacitor_values)
            circuit = LcapyCircuit(netlist)
            
            # Draw with professional settings
            # lcapy.draw() creates and modifies the current matplotlib figure
            circuit.draw(
                draw_nodes='none',          # Hide internal node markers
                label_nodes=False,          # Don't label nodes
                label_values=True,          # Show capacitance values
                style='american',           # Use American circuit symbols
                scale=1.5,                  # Larger scale for more spacing
                node_spacing=2.5,           # More space between nodes
                cpt_size=1.2,               # Component size
                font_size=9,                # Smaller font to prevent overlap
                dpi=300                     # High resolution
            )
            
            # Get the figure lcapy created and improve appearance
            fig = plt.gcf()
            fig.set_size_inches(14, 5)            # Wider for more space
            fig.patch.set_facecolor('white')      # White background
            for ax in fig.get_axes():
                ax.set_aspect('equal')            # Equal aspect ratio
                ax.margins(0.1)                   # Add 10% margin around content
            fig.tight_layout(pad=1.0)             # More padding
            return fig
            
        except Exception as e:
            logger.warning(f"Lcapy rendering failed: {e}, using schemdraw fallback")
    
    # Fallback to schemdraw rendering
    if not SCHEMDRAW_AVAILABLE:
        raise ImportError(
            "Neither lcapy nor schemdraw available for circuit rendering. "
            "Install with: pip install lcapy or pip install schemdraw"
        )

    # Create drawing with appropriate unit size
    drawing = schemdraw.Drawing()

    # Add terminal A at the start with colored label
    drawing += elm.Dot().label('A', loc='left', color=TERMINAL_COLOR)

    # Recursively build circuit
    _draw_sp_recursive(drawing, node, capacitor_labels, capacitor_values)

    # Add terminal B at the end with colored label
    drawing += elm.Dot().label('B', loc='right', color=TERMINAL_COLOR)

    # Get the matplotlib figure - schemdraw returns different objects depending on version
    result = drawing.draw(show=False)
    
    # Handle different schemdraw versions (0.15 returns schemdraw.Figure with .fig attribute)
    if hasattr(result, 'fig'):
        # schemdraw 0.15+: result is schemdraw.backends.mpl.Figure
        fig = result.fig
    elif isinstance(result, plt.Figure):
        # Some versions return matplotlib Figure directly
        fig = result
    else:
        # Fallback: create new figure
        fig, ax = plt.subplots(figsize=(10, 6))
        drawing.draw(ax=ax, show=False)
    
    # Expand axis limits to add padding for labels
    if fig.axes:
        ax = fig.axes[0]
        
        # Vertical padding (for capacitor labels on top)
        ylim = ax.get_ylim()
        y_range = ylim[1] - ylim[0]
        min_y_padding = 1.0  # Minimum padding in drawing units
        top_padding = max(y_range * 0.25, min_y_padding)
        bottom_padding = max(y_range * 0.15, min_y_padding * 0.6)
        ax.set_ylim(ylim[0] - bottom_padding, ylim[1] + top_padding)
        
        # Horizontal padding (for terminal labels A and B)
        xlim = ax.get_xlim()
        x_range = xlim[1] - xlim[0]
        min_x_padding = 0.8  # Minimum padding for terminal labels
        left_padding = max(x_range * 0.05, min_x_padding)
        right_padding = max(x_range * 0.05, min_x_padding)
        ax.set_xlim(xlim[0] - left_padding, xlim[1] + right_padding)
    
    return fig


def _draw_sp_recursive(
    drawing: Any,
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: Optional[List[float]] = None
) -> None:
    """Recursively draw SP node structure onto SchemDraw drawing.

    Args:
        drawing: SchemDraw Drawing object to add elements to.
        node: Current SPNode to render.
        capacitor_labels: Labels for capacitors.
        capacitor_values: Optional values for display in labels.
    """
    if isinstance(node, Leaf):
        # Base case: Draw single capacitor
        label = capacitor_labels[node.capacitor_index]

        # Format label with value if provided
        if capacitor_values is not None:
            value = capacitor_values[node.capacitor_index]
            value_str = _format_capacitance(value)
            full_label = f"{label}\n{value_str}"  # Two lines for better readability
        else:
            full_label = label

        # Draw capacitor horizontally with styled label (white background for visibility)
        drawing += elm.Capacitor().right().label(
            full_label, 
            loc='top', 
            color=LABEL_COLOR,
            fontsize=7
        ).label(
            '',  # Empty label to create space
            loc='bottom'
        )

    elif isinstance(node, Series):
        # Series: Draw left then right sequentially (horizontal chain)
        _draw_sp_recursive(drawing, node.left, capacitor_labels, capacitor_values)
        _draw_sp_recursive(drawing, node.right, capacitor_labels, capacitor_values)

    elif isinstance(node, Parallel):
        # Parallel: Split into branches, draw each, then join
        # Save current position (start of parallel section)
        split_point = drawing.here
        split_y = split_point[1]

        # Draw top branch (left subtree)
        drawing.push()  # Save state
        _draw_sp_recursive(drawing, node.left, capacitor_labels, capacitor_values)
        top_end = drawing.here
        drawing.pop()  # Restore state

        # Draw bottom branch (right subtree)
        drawing += elm.Line().down(1.5)  # Move down to create vertical separation
        _draw_sp_recursive(drawing, node.right, capacitor_labels, capacitor_values)
        bottom_end = drawing.here

        # Join branches - move to end position
        # Calculate the rightmost x-position (where branches should merge)
        end_x = max(top_end[0], bottom_end[0])
        # Calculate midpoint y-coordinate for join
        join_y = (top_end[1] + bottom_end[1]) / 2

        # Connect top branch to join point
        drawing.here = top_end
        if end_x > top_end[0]:
            drawing += elm.Line().right(end_x - top_end[0])
        # Draw to join point (may need to go down)
        if top_end[1] > join_y:
            drawing += elm.Line().to((end_x, join_y))

        # Connect bottom branch to join point
        drawing.here = bottom_end
        if end_x > bottom_end[0]:
            drawing += elm.Line().right(end_x - bottom_end[0])
        # Draw to join point (may need to go up)
        if bottom_end[1] < join_y:
            drawing += elm.Line().to((end_x, join_y))

        # Set position to merged point for continuation
        drawing.here = (end_x, join_y)

    else:
        raise TypeError(f"Unknown SPNode type: {type(node)}")


def _format_capacitance(value: float) -> str:
    """Format capacitance value with appropriate unit.

    Chooses unit (pF, nF, µF, mF, F) based on magnitude.

    Args:
        value: Capacitance in Farads.

    Returns:
        Formatted string with unit (e.g., "5.2pF", "1.5nF").

    Examples:
        >>> _format_capacitance(5.2e-12)
        '5.2pF'
        >>> _format_capacitance(1.5e-9)
        '1.5nF'
        >>> _format_capacitance(2.7e-6)
        '2.7µF'
    """
    if value == 0:
        return "0F"

    abs_value = abs(value)

    # Choose appropriate unit
    if abs_value < 1e-9:  # < 1nF
        return f"{value * 1e12:.4g}pF"
    elif abs_value < 1e-6:  # < 1µF
        return f"{value * 1e9:.4g}nF"
    elif abs_value < 1e-3:  # < 1mF
        return f"{value * 1e6:.4g}µF"
    elif abs_value < 1:  # < 1F
        return f"{value * 1e3:.4g}mF"
    else:
        return f"{value:.4g}F"


def _format_capacitance_for_netlist(value_farads: float) -> str:
    """Format capacitance value for lcapy netlist.
    
    Returns capacitance in scientific notation format that lcapy can parse.
    Lcapy requires plain numeric values or scientific notation (e.g., "1.5e-5")
    and does NOT accept SPICE suffix notation like "15uF" or "3.3nF".
    
    Args:
        value_farads: Capacitance in Farads
        
    Returns:
        Formatted string in scientific notation (e.g., "1.5e-5", "3.3e-9")
        
    Examples:
        >>> _format_capacitance_for_netlist(1.5e-05)
        '1.5e-05'
        >>> _format_capacitance_for_netlist(3.3e-09)
        '3.3e-09'
        >>> _format_capacitance_for_netlist(4.7e-12)
        '4.7e-12'
    
    Constitutional Compliance:
        - Principle I (Scientific Accuracy): Uses standard scientific notation
    """
    # Return scientific notation format that lcapy accepts
    # Use %.6g format to avoid unnecessary trailing zeros
    return f"{value_farads:.6g}"


def _sp_to_lcapy_netlist_recursive(
    node: SPNode,
    in_node: int,
    out_node: int,
    capacitors: List[float],
    labels: List[str],
    next_node_ref: List[int],
    lines: List[str]
) -> None:
    """Recursively convert SPNode to netlist lines.
    
    Traverses SP tree structure and generates SPICE-format netlist lines.
    Node numbering: Terminal A = 1, Terminal B = 0, internal nodes = 2, 3, ...
    
    Args:
        node: Current SPNode (Leaf, Series, or Parallel)
        in_node: Input node number
        out_node: Output node number
        capacitors: Capacitance values in Farads
        labels: Capacitor labels (e.g., ["C1", "C2"])
        next_node_ref: [next_available_node] (mutable counter)
        lines: Accumulated netlist lines (mutable list)
        
    Constitutional Compliance:
        - Principle VI (Algorithmic Correctness): Preserves circuit topology
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
        
        _sp_to_lcapy_netlist_recursive(node.left, in_node, mid_node,
                                       capacitors, labels, next_node_ref, lines)
        _sp_to_lcapy_netlist_recursive(node.right, mid_node, out_node,
                                       capacitors, labels, next_node_ref, lines)
        
    elif isinstance(node, Parallel):
        # Parallel: both connect in to out
        _sp_to_lcapy_netlist_recursive(node.left, in_node, out_node,
                                       capacitors, labels, next_node_ref, lines)
        _sp_to_lcapy_netlist_recursive(node.right, in_node, out_node,
                                       capacitors, labels, next_node_ref, lines)
    else:
        raise TypeError(f"Unknown SPNode type: {type(node)}")


def sp_to_lcapy_netlist(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: List[float]
) -> str:
    """Convert SPNode tree to lcapy netlist format.
    
    Generates SPICE-format netlist with proper node numbering convention:
    - Terminal A = node 1
    - Terminal B = node 0 (ground)
    - Internal nodes = 2, 3, 4, ...
    
    Args:
        node: Root SPNode
        capacitor_labels: Labels for capacitors (e.g., ["C1", "C2"])
        capacitor_values: Capacitance values in Farads
        
    Returns:
        Multiline netlist string
        
    Examples:
        >>> node = Series(Leaf(0, 1e-05), Leaf(1, 5e-06))
        >>> netlist = sp_to_lcapy_netlist(node, ["C1", "C2"], [1e-05, 5e-06])
        >>> print(netlist)
        C1 1 2 10uF
        C2 2 0 5uF
        
    Constitutional Compliance:
        - Principle VI (Algorithmic Correctness): Accurate topology conversion
    """
    lines = []
    next_node_ref = [2]  # Start internal nodes at 2
    
    # Terminal A = node 1, Terminal B = node 0
    _sp_to_lcapy_netlist_recursive(node, 1, 0, capacitor_values, 
                                   capacitor_labels, next_node_ref, lines)
    
    return "\n".join(lines)


def graph_to_lcapy_netlist(
    topology: GraphTopology,
    capacitor_labels: Optional[List[str]] = None
) -> str:
    """Convert GraphTopology to lcapy netlist format.
    
    Generates SPICE-format netlist for general graph topologies, including
    proper handling of parallel edges (MultiGraph).
    
    Node numbering convention:
    - Terminal A = node 1
    - Terminal B = node 0 (ground)
    - Internal nodes = 2, 3, 4, ...
    
    Args:
        topology: GraphTopology with NetworkX graph
        capacitor_labels: Optional custom labels
        
    Returns:
        Multiline netlist string
        
    Examples:
        >>> G = nx.MultiGraph()
        >>> G.add_edge('A', 'B', capacitance=1e-05)
        >>> topology = GraphTopology(G, 'A', 'B', [])
        >>> netlist = graph_to_lcapy_netlist(topology)
        >>> print(netlist)
        CAB 1 0 10uF
        
    Constitutional Compliance:
        - Principle VI (Algorithmic Correctness): Preserves graph structure
    """
    graph = topology.graph
    
    # Create node mapping: A→1, B→0, internal→2+
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
    
    # Check if MultiGraph or regular Graph
    is_multigraph = isinstance(graph, nx.MultiGraph)
    
    if is_multigraph:
        # MultiGraph: iterate with keys to handle parallel edges
        for u, v, key, data in graph.edges(keys=True, data=True):
            cap = data.get('capacitance', 0)
            cap_str = _format_capacitance_for_netlist(cap)
            
            # Generate unique label for edge (handle parallel edges)
            pair = tuple(sorted([u, v]))
            edge_num = edge_count.get(pair, 0)
            edge_count[pair] = edge_num + 1
            
            # Create label: CAB, CAB_1, CAB_2, etc.
            if edge_num == 0:
                label = f"C{u}{v}"
            else:
                label = f"C{u}{v}_{edge_num}"
            
            # Clean label (remove special characters)
            label = label.replace(" ", "").replace("-", "")
            
            node1 = node_map[u]
            node2 = node_map[v]
            
            lines.append(f"{label} {node1} {node2} {cap_str}")
    else:
        # Regular Graph: no keys parameter
        for u, v, data in graph.edges(data=True):
            cap = data.get('capacitance', 0)
            cap_str = _format_capacitance_for_netlist(cap)
            
            # Generate unique label for edge
            pair = tuple(sorted([u, v]))
            edge_num = edge_count.get(pair, 0)
            edge_count[pair] = edge_num + 1
            
            # Create label: CAB, CAB_1, CAB_2, etc.
            if edge_num == 0:
                label = f"C{u}{v}"
            else:
                label = f"C{u}{v}_{edge_num}"
            
            # Clean label (remove special characters)
            label = label.replace(" ", "").replace("-", "")
            
            node1 = node_map[u]
            node2 = node_map[v]
            
            lines.append(f"{label} {node1} {node2} {cap_str}")
    
    return "\n".join(lines)


def draw_graph(
    graph: Dict[str, Any],
    scale: float = 0.6,
    font: int = 8
) -> plt.Figure:
    """Draw general network topology using NetworkX.

    Creates a graph visualization with nodes and edges labeled with
    capacitance values.

    Args:
        graph: Dictionary describing the network topology.
        scale: Scaling factor for the diagram.
        font: Font size for labels.

    Returns:
        Matplotlib figure containing the network graph.

    Note:
        Requires NetworkX library for graph visualization.
    """
    # Placeholder implementation - superseded by render_graph_network
    pass


def render_graph_network(
    topology: GraphTopology,
    scale: float = 1.0,
    font_size: int = 10
) -> plt.Figure:
    """Render general graph network as professional circuit schematic.

    Uses lcapy for professional CircuiTikZ-quality diagrams. If lcapy is
    unavailable or rendering fails, falls back to matplotlib rendering.

    Creates a circuit-style diagram with nodes as connection points and
    capacitors as edges.

    Args:
        topology: GraphTopology object with graph, terminals, and internal nodes.
        scale: Scaling factor for the diagram layout.
        font_size: Font size for labels.

    Returns:
        Matplotlib figure containing the circuit schematic.

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'n1', capacitance=5e-12)
        >>> G.add_edge('n1', 'B', capacitance=10e-12)
        >>> topology = GraphTopology(G, 'A', 'B', ['n1'])
        >>> fig = render_graph_network(topology)
        
    Constitutional Compliance:
        - Principle II (UX First): Clear graph visualization
        - Principle IV (Modular Architecture): Pure rendering function
    """
    # Try lcapy rendering first (professional quality)
    if LCAPY_AVAILABLE:
        try:
            netlist = graph_to_lcapy_netlist(topology)
            circuit = LcapyCircuit(netlist)
            
            # Draw with configuration for graphs (show internal nodes)
            # lcapy.draw() creates and modifies the current matplotlib figure
            circuit.draw(
                draw_nodes='connections',   # Show internal connection nodes
                label_nodes=True,           # Label internal nodes
                label_values=True,          # Show capacitance values
                style='american',           # Use American circuit symbols
                scale=max(1.5, scale),      # Larger scale for more spacing
                node_spacing=2.5,           # More space between nodes
                cpt_size=1.2,               # Component size
                font_size=9,                # Smaller font to prevent overlap
                dpi=300                     # High resolution
            )
            
            # Get the figure lcapy created and improve appearance
            fig = plt.gcf()
            fig.set_size_inches(16, 7)            # Larger for more space
            fig.patch.set_facecolor('white')      # White background
            for ax in fig.get_axes():
                ax.set_aspect('equal')            # Equal aspect ratio
                ax.margins(0.1)                   # Add 10% margin around content
            fig.tight_layout(pad=1.0)             # More padding
            return fig
            
        except Exception as e:
            logger.warning(f"Lcapy graph rendering failed: {e}, using matplotlib fallback")
    
    # Fallback to matplotlib rendering
    graph = topology.graph

    # Try to use SchemDraw for proper circuit rendering
    if SCHEMDRAW_AVAILABLE:
        return _render_graph_as_circuit_schemdraw(topology, font_size)
    else:
        return _render_graph_as_circuit_matplotlib(topology, scale, font_size)


def _render_graph_as_circuit_schemdraw(
    topology: GraphTopology,
    font_size: int = 10
) -> plt.Figure:
    """Render graph topology as circuit using SchemDraw.
    
    Uses a grid-based layout to position nodes and draw capacitors between them.
    """
    graph = topology.graph
    
    # Create drawing
    drawing = schemdraw.Drawing()
    
    # Use hierarchical layout: A on left, B on right, internal nodes in middle
    nodes = list(graph.nodes())
    n_internal = len(topology.internal_nodes)
    
    # Position dictionary for nodes
    node_positions = {}
    
    # Position terminals
    node_positions[topology.terminal_a] = (0, 0)
    node_positions[topology.terminal_b] = (6, 0)  # Right side
    
    # Position internal nodes in a grid between A and B
    if n_internal > 0:
        # Arrange internal nodes vertically centered
        for i, node in enumerate(topology.internal_nodes):
            x = 3  # Middle
            y = (i - (n_internal - 1) / 2) * 1.5  # Spread vertically
            node_positions[node] = (x, y)
    
    # Track which edges we've drawn
    drawn_edges = set()
    
    # Draw terminal A
    drawing += elm.Dot().at(node_positions[topology.terminal_a]).label(
        topology.terminal_a, loc='left', color=TERMINAL_COLOR, fontsize=font_size + 2
    )
    
    # Draw all edges as capacitors
    edge_labels = []
    for u, v, data in graph.edges(data=True):
        edge_key = tuple(sorted([u, v]))
        if edge_key in drawn_edges:
            continue
        drawn_edges.add(edge_key)
        
        cap = data.get('capacitance', 0)
        cap_label = _format_capacitance(cap)
        
        pos_u = node_positions[u]
        pos_v = node_positions[v]
        
        # Draw line from u to capacitor midpoint, then capacitor, then to v
        mid_x = (pos_u[0] + pos_v[0]) / 2
        mid_y = (pos_u[1] + pos_v[1]) / 2
        
        # Store edge info for labeling
        edge_labels.append((mid_x, mid_y, cap_label, u, v))
    
    # Draw internal nodes
    for node in topology.internal_nodes:
        pos = node_positions[node]
        drawing += elm.Dot().at(pos).label(
            str(node), loc='top', color='#2C3E50', fontsize=font_size
        )
    
    # Draw terminal B
    drawing += elm.Dot().at(node_positions[topology.terminal_b]).label(
        topology.terminal_b, loc='right', color=TERMINAL_COLOR, fontsize=font_size + 2
    )
    
    # Get base figure from schemdraw
    result = drawing.draw(show=False)
    if hasattr(result, 'fig'):
        base_fig = result.fig
    elif isinstance(result, plt.Figure):
        base_fig = result
    else:
        base_fig, _ = plt.subplots(figsize=(10, 6))
    
    # Now overlay with matplotlib for more control
    return _render_graph_as_circuit_matplotlib(topology, 1.0, font_size)


def _render_graph_as_circuit_matplotlib(
    topology: GraphTopology,
    scale: float = 1.0,
    font_size: int = 10
) -> plt.Figure:
    """Render graph topology as circuit schematic using matplotlib.
    
    Creates a clean circuit-like diagram with capacitor symbols on edges.
    """
    graph = topology.graph
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create custom layout: terminals on sides, internal nodes in middle
    pos = {}
    nodes = list(graph.nodes())
    n_internal = len(topology.internal_nodes)
    
    # Position terminals on left and right
    pos[topology.terminal_a] = (-2.0 * scale, 0)
    pos[topology.terminal_b] = (2.0 * scale, 0)
    
    # Position internal nodes in the middle, spread vertically
    for i, node in enumerate(topology.internal_nodes):
        y = (i - (n_internal - 1) / 2) * 0.8 * scale if n_internal > 1 else 0
        pos[node] = (0, y)
    
    # Draw edges as capacitor symbols
    # Handle both MultiGraph (with keys) and regular Graph (without keys)
    edge_count = {}  # Track how many edges between each pair for offset
    is_multigraph = isinstance(graph, nx.MultiGraph)
    
    if is_multigraph:
        # MultiGraph: iterate with keys to get all parallel edges
        for u, v, key, data in graph.edges(data=True, keys=True):
            cap = data.get('capacitance', 0)
            cap_label = _format_capacitance(cap)
            
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Calculate offset for parallel edges
            pair = tuple(sorted([u, v]))
            edge_num = edge_count.get(pair, 0)
            edge_count[pair] = edge_num + 1
            
            # Draw wire segments with capacitor symbol in middle
            _draw_capacitor_symbol(ax, x1, y1, x2, y2, cap_label, font_size, edge_num)
    else:
        # Regular Graph: no keys parameter
        for u, v, data in graph.edges(data=True):
            cap = data.get('capacitance', 0)
            cap_label = _format_capacitance(cap)
            
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            
            # Calculate offset for parallel edges (shouldn't happen in regular Graph)
            pair = tuple(sorted([u, v]))
            edge_num = edge_count.get(pair, 0)
            edge_count[pair] = edge_num + 1
            
            # Draw wire segments with capacitor symbol in middle
            _draw_capacitor_symbol(ax, x1, y1, x2, y2, cap_label, font_size, edge_num)
    
    # Draw nodes as dots
    for node in graph.nodes():
        x, y = pos[node]
        
        if node == topology.terminal_a:
            color = TERMINAL_COLOR
            size = 150
            label = 'A'
        elif node == topology.terminal_b:
            color = TERMINAL_COLOR
            size = 150
            label = 'B'
        else:
            color = '#2C3E50'
            size = 80
            label = str(node)
        
        ax.scatter([x], [y], s=size, c=color, zorder=10, edgecolors='white', linewidths=2)
        
        # Add node label
        offset_y = 0.15 if node in (topology.terminal_a, topology.terminal_b) else 0.12
        ax.text(x, y - offset_y, label, ha='center', va='top',
                fontsize=font_size + 1, fontweight='bold', color=color,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                         edgecolor=color, alpha=0.9))
    
    # Title
    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()
    ax.set_title(
        f"Circuit Network: {n_edges} capacitors, {n_nodes - 2} internal nodes\n"
        f"Terminals: {topology.terminal_a} → {topology.terminal_b}",
        fontsize=font_size + 2,
        fontweight='bold',
        color='#2C3E50',
        pad=20
    )
    
    # Clean up axes
    ax.set_aspect('equal')
    ax.autoscale()
    margin = 0.5
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.set_xlim(xlim[0] - margin, xlim[1] + margin)
    ax.set_ylim(ylim[0] - margin, ylim[1] + margin)
    ax.axis('off')
    
    plt.tight_layout()
    return fig


def _draw_capacitor_symbol(
    ax: plt.Axes,
    x1: float, y1: float,
    x2: float, y2: float,
    label: str,
    font_size: int = 10,
    edge_num: int = 0
) -> None:
    """Draw a capacitor symbol between two points.
    
    Draws connecting wires and a capacitor symbol (two parallel lines) in the middle.
    For parallel edges (edge_num > 0), draws curved path.
    
    Args:
        edge_num: Index for parallel edges (0 for first, 1 for second, etc.) to offset them
    """
    import numpy as np
    from matplotlib.patches import FancyBboxPatch, Arc
    from matplotlib.path import Path
    import matplotlib.patches as mpatches
    
    # Calculate direction and perpendicular
    dx = x2 - x1
    dy = y2 - y1
    length = np.sqrt(dx**2 + dy**2)
    
    if length < 0.01:
        return
    
    # Unit vectors
    ux, uy = dx / length, dy / length  # Direction along edge
    px, py = -uy, ux  # Perpendicular
    
    # Capacitor plate dimensions
    plate_width = 0.08  # Width of capacitor plate
    plate_gap = 0.06    # Gap between plates
    
    # For parallel edges, use curved path
    if edge_num > 0:
        # Calculate arc control point (offset perpendicular to edge)
        curve_offset = 0.3 * edge_num  # How much to curve
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ctrl_x = mid_x + px * curve_offset
        ctrl_y = mid_y + py * curve_offset
        
        # Create curved path using quadratic Bezier
        verts = [
            (x1, y1),
            (ctrl_x, ctrl_y),
            (x2, y2)
        ]
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)
        
        # Draw curved wire
        patch = mpatches.PathPatch(path, facecolor='none', edgecolor='#2C3E50', 
                                   linewidth=2, zorder=1)
        ax.add_patch(patch)
        
        # Draw capacitor symbol at curve midpoint
        # Use control point as capacitor location
        mx, my = ctrl_x, ctrl_y
        
        # Draw capacitor plates perpendicular to curve at midpoint
        plate1_x = [mx - px * plate_width, mx + px * plate_width]
        plate1_y = [my - py * plate_width, my + py * plate_width]
        ax.plot(plate1_x, plate1_y, color='#2C3E50', linewidth=3, zorder=2)
        
        # Add label
        label_offset = 0.15
        label_x = mx + px * label_offset
        label_y = my + py * label_offset
        
        ax.text(label_x, label_y, label, ha='center', va='center',
                fontsize=font_size, fontweight='bold', color=LABEL_COLOR,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=LABEL_COLOR, alpha=0.95),
                zorder=5)
        return
    
    # Midpoint
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    
    # Draw wire from point 1 to first plate
    wire1_end_x = mx - ux * plate_gap
    wire1_end_y = my - uy * plate_gap
    ax.plot([x1, wire1_end_x], [y1, wire1_end_y], 
            color='#2C3E50', linewidth=2, zorder=1)
    
    # Draw wire from second plate to point 2
    wire2_start_x = mx + ux * plate_gap
    wire2_start_y = my + uy * plate_gap
    ax.plot([wire2_start_x, x2], [wire2_start_y, y2], 
            color='#2C3E50', linewidth=2, zorder=1)
    
    # Draw first capacitor plate (perpendicular to edge)
    plate1_x = [wire1_end_x - px * plate_width, wire1_end_x + px * plate_width]
    plate1_y = [wire1_end_y - py * plate_width, wire1_end_y + py * plate_width]
    ax.plot(plate1_x, plate1_y, color='#2C3E50', linewidth=3, zorder=2)
    
    # Draw second capacitor plate
    plate2_x = [wire2_start_x - px * plate_width, wire2_start_x + px * plate_width]
    plate2_y = [wire2_start_y - py * plate_width, wire2_start_y + py * plate_width]
    ax.plot(plate2_x, plate2_y, color='#2C3E50', linewidth=3, zorder=2)
    
    # Add capacitance label with white background
    # Position label slightly offset from the capacitor
    label_offset = 0.15
    label_x = mx + px * label_offset
    label_y = my + py * label_offset
    
    ax.text(label_x, label_y, label, ha='center', va='center',
            fontsize=font_size, fontweight='bold', color=LABEL_COLOR,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor=LABEL_COLOR, alpha=0.95),
            zorder=5)


def plot_error_distribution(
    solutions: List[Tuple[Any, float]],
    target: float
) -> plt.Figure:
    """Plot histogram of error distribution for solutions.

    Args:
        solutions: List of (topology, capacitance) tuples.
        target: Target capacitance value.

    Returns:
        Matplotlib figure with error distribution histogram.
    """
    # Placeholder implementation
    pass


# =============================================================================
# LaTeX / CircuiTikZ Code Generation
# =============================================================================

def generate_sp_latex(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: Optional[List[float]] = None
) -> str:
    """Generate LaTeX code using CircuiTikZ for SP circuit.

    Creates complete LaTeX code that can be compiled with pdflatex.
    Uses the circuitikz package for professional circuit diagrams.

    Args:
        node: Root SPNode of the network topology.
        capacitor_labels: Labels for capacitors (e.g., ["C1", "C2", "C3"]).
        capacitor_values: Optional list of capacitance values for display.

    Returns:
        Complete LaTeX document string ready for compilation.

    Example:
        >>> leaf = Leaf(0, 5e-12)
        >>> latex = generate_sp_latex(leaf, ["C1"], [5e-12])
        >>> # Returns complete LaTeX document with circuitikz diagram
    """
    # Generate the circuit body
    circuit_body = _generate_sp_latex_recursive(node, capacitor_labels, capacitor_values, 0, 0)
    
    # Wrap in complete LaTeX document
    latex_code = r"""\documentclass[border=10pt]{standalone}
\usepackage[siunitx, RPvoltages]{circuitikz}
\usepackage{siunitx}

\begin{document}
\begin{circuitikz}[american]
    % Terminal A
    \draw (0,0) node[circ, label=left:A] {};
    
    % Circuit body
""" + circuit_body + r"""
    
    % Terminal B (end point)
    \draw (end) node[circ, label=right:B] {};
\end{circuitikz}
\end{document}
"""
    return latex_code


def _generate_sp_latex_recursive(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: Optional[List[float]],
    x: float,
    y: float,
    depth: int = 0
) -> str:
    """Recursively generate CircuiTikZ code for SP topology.
    
    Args:
        node: Current SPNode.
        capacitor_labels: Labels for capacitors.
        capacitor_values: Optional values for labels.
        x: Current x position.
        y: Current y position.
        depth: Recursion depth for naming.
    
    Returns:
        CircuiTikZ draw commands as string.
    """
    if isinstance(node, Leaf):
        # Single capacitor
        label = capacitor_labels[node.capacitor_index]
        if capacitor_values is not None:
            value = capacitor_values[node.capacitor_index]
            value_str = _format_capacitance_latex(value)
            cap_label = f"{label}={value_str}"
        else:
            cap_label = label
        
        return f"    \\draw ({x},{y}) to[C, l={{{cap_label}}}] ++(2,0) coordinate (end);\n"
    
    elif isinstance(node, Series):
        # Series: draw left, then right from endpoint
        left_code = _generate_sp_latex_recursive(
            node.left, capacitor_labels, capacitor_values, x, y, depth + 1
        )
        # For series, continue from 'end' coordinate
        right_code = _generate_sp_latex_recursive(
            node.right, capacitor_labels, capacitor_values, 0, 0, depth + 1
        )
        # Replace start position with (end) for right side
        right_code = right_code.replace(f"\\draw (0,0)", "\\draw (end)", 1)
        return left_code + right_code
    
    elif isinstance(node, Parallel):
        # Parallel: split into two branches
        lines = []
        lines.append(f"    \\draw ({x},{y}) coordinate (split{depth});")
        
        # Top branch (left subtree)
        top_code = _generate_sp_latex_recursive(
            node.left, capacitor_labels, capacitor_values, 0, 0.5, depth + 1
        )
        top_code = top_code.replace("\\draw (0,0.5)", f"\\draw (split{depth}) -- ++(0,0.5) coordinate (top{depth}) to[C", 1)
        top_code = top_code.replace("to[C,", "to[C,")
        
        # Bottom branch (right subtree)  
        bot_code = _generate_sp_latex_recursive(
            node.right, capacitor_labels, capacitor_values, 0, -0.5, depth + 1
        )
        bot_code = bot_code.replace("\\draw (0,-0.5)", f"\\draw (split{depth}) -- ++(0,-0.5) coordinate (bot{depth}) to[C", 1)
        
        # Simplified parallel structure
        left_label = _get_node_label(node.left, capacitor_labels, capacitor_values)
        right_label = _get_node_label(node.right, capacitor_labels, capacitor_values)
        
        parallel_code = f"""    \\draw ({x},{y}) coordinate (split{depth})
        (split{depth}) -- ++(0,0.5) to[C, l={{{left_label}}}] ++(2,0) coordinate (topend{depth})
        (split{depth}) -- ++(0,-0.5) to[C, l={{{right_label}}}] ++(2,0) coordinate (botend{depth})
        (topend{depth}) -- ++(0,-0.5) coordinate (end)
        (botend{depth}) -- ++(0,0.5);
"""
        return parallel_code
    
    return ""


def _get_node_label(
    node: SPNode,
    capacitor_labels: List[str],
    capacitor_values: Optional[List[float]]
) -> str:
    """Get label for a node (for simple display in parallel branches)."""
    if isinstance(node, Leaf):
        label = capacitor_labels[node.capacitor_index]
        if capacitor_values is not None:
            value = capacitor_values[node.capacitor_index]
            value_str = _format_capacitance_latex(value)
            return f"{label}={value_str}"
        return label
    elif isinstance(node, Series):
        left = _get_node_label(node.left, capacitor_labels, capacitor_values)
        right = _get_node_label(node.right, capacitor_labels, capacitor_values)
        return f"({left} + {right})"
    elif isinstance(node, Parallel):
        left = _get_node_label(node.left, capacitor_labels, capacitor_values)
        right = _get_node_label(node.right, capacitor_labels, capacitor_values)
        return f"({left} || {right})"
    return "?"


def _format_capacitance_latex(value: float) -> str:
    """Format capacitance value for LaTeX with siunitx.
    
    Args:
        value: Capacitance in Farads.
    
    Returns:
        LaTeX formatted string using siunitx.
    """
    if value == 0:
        return r"\SI{0}{\farad}"
    
    abs_value = abs(value)
    
    if abs_value < 1e-9:  # < 1nF -> pF
        return f"\\SI{{{value * 1e12:.4g}}}{{\\pico\\farad}}"
    elif abs_value < 1e-6:  # < 1µF -> nF
        return f"\\SI{{{value * 1e9:.4g}}}{{\\nano\\farad}}"
    elif abs_value < 1e-3:  # < 1mF -> µF
        return f"\\SI{{{value * 1e6:.4g}}}{{\\micro\\farad}}"
    elif abs_value < 1:  # < 1F -> mF
        return f"\\SI{{{value * 1e3:.4g}}}{{\\milli\\farad}}"
    else:
        return f"\\SI{{{value:.4g}}}{{\\farad}}"


def generate_graph_latex(topology: GraphTopology) -> str:
    """Generate LaTeX code using CircuiTikZ for graph topology.

    Creates complete LaTeX code for general graph networks.

    Args:
        topology: GraphTopology object.

    Returns:
        Complete LaTeX document string ready for compilation.
    """
    graph = topology.graph
    
    # Position nodes
    nodes = list(graph.nodes())
    n_internal = len(topology.internal_nodes)
    
    # Create node positions
    node_positions = {}
    node_positions[topology.terminal_a] = (0, 0)
    node_positions[topology.terminal_b] = (6, 0)
    
    for i, node in enumerate(topology.internal_nodes):
        y = (i - (n_internal - 1) / 2) * 1.5 if n_internal > 1 else 0
        node_positions[node] = (3, y)
    
    # Generate node definitions
    node_defs = []
    for node, (x, y) in node_positions.items():
        if node == topology.terminal_a:
            node_defs.append(f"    \\node[circ, label=left:A] (A) at ({x},{y}) {{}};")
        elif node == topology.terminal_b:
            node_defs.append(f"    \\node[circ, label=right:B] (B) at ({x},{y}) {{}};")
        else:
            node_defs.append(f"    \\node[circ, label=above:{node}] ({node}) at ({x},{y}) {{}};")
    
    # Generate edges (capacitors)
    edge_defs = []
    for u, v, data in graph.edges(data=True):
        cap = data.get('capacitance', 0)
        cap_label = _format_capacitance_latex(cap)
        edge_defs.append(f"    \\draw ({u}) to[C, l={{{cap_label}}}] ({v});")
    
    # Assemble document
    latex_code = r"""\documentclass[border=10pt]{standalone}
\usepackage[siunitx, RPvoltages]{circuitikz}
\usepackage{siunitx}

\begin{document}
\begin{circuitikz}[american]
    % Nodes
""" + "\n".join(node_defs) + r"""
    
    % Capacitors (edges)
""" + "\n".join(edge_defs) + r"""
\end{circuitikz}
\end{document}
"""
    return latex_code


def generate_latex_code(
    topology,
    capacitor_labels: Optional[List[str]] = None,
    capacitor_values: Optional[List[float]] = None
) -> str:
    """Generate LaTeX/CircuiTikZ code for any topology type.

    Automatically detects whether the topology is SP or Graph and
    generates appropriate LaTeX code.

    Args:
        topology: SPNode or GraphTopology object.
        capacitor_labels: Labels for capacitors (required for SP).
        capacitor_values: Optional values for display.

    Returns:
        Complete LaTeX document string.
    """
    if isinstance(topology, GraphTopology):
        return generate_graph_latex(topology)
    elif isinstance(topology, (Leaf, Series, Parallel)):
        if capacitor_labels is None:
            # Generate default labels
            indices = _collect_indices(topology)
            capacitor_labels = [f"C{i+1}" for i in range(max(indices) + 1)]
        return generate_sp_latex(topology, capacitor_labels, capacitor_values)
    else:
        return "% Unknown topology type"


def _collect_indices(node: SPNode) -> set:
    """Collect all capacitor indices from SP tree."""
    if isinstance(node, Leaf):
        return {node.capacitor_index}
    elif isinstance(node, (Series, Parallel)):
        return _collect_indices(node.left) | _collect_indices(node.right)
    return set()

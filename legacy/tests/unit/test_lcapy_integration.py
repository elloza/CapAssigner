"""
Tests for lcapy circuit visualization integration.

Tests the conversion of SPNode and GraphTopology structures to lcapy netlist format
and rendering functions. Tests are skipped if lcapy is not installed.
"""

import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for testing
import matplotlib.pyplot as plt
import networkx as nx

# Check lcapy availability
try:
    import lcapy
    LCAPY_AVAILABLE = True
except ImportError:
    LCAPY_AVAILABLE = False

from capassigner.core.sp_structures import Leaf, Series, Parallel
from capassigner.core.graphs import GraphTopology


# Skip all tests if lcapy not available
pytestmark = pytest.mark.skipif(not LCAPY_AVAILABLE, reason="lcapy not installed")


class TestCapacitanceFormatting:
    """Test capacitance value formatting for netlist (scientific notation)."""
    
    def test_format_microfarad(self):
        """Test formatting values in microfarad range."""
        from capassigner.ui.plots import _format_capacitance_for_netlist
        assert _format_capacitance_for_netlist(1.5e-05) == "1.5e-05"
        assert _format_capacitance_for_netlist(1e-05) == "1e-05"
        assert _format_capacitance_for_netlist(3.3e-06) == "3.3e-06"
    
    def test_format_nanofarad(self):
        """Test formatting values in nanofarad range."""
        from capassigner.ui.plots import _format_capacitance_for_netlist
        assert _format_capacitance_for_netlist(3.3e-09) == "3.3e-09"
        assert _format_capacitance_for_netlist(1e-09) == "1e-09"
        assert _format_capacitance_for_netlist(4.7e-09) == "4.7e-09"
    
    def test_format_picofarad(self):
        """Test formatting values in picofarad range."""
        from capassigner.ui.plots import _format_capacitance_for_netlist
        assert _format_capacitance_for_netlist(4.7e-12) == "4.7e-12"
        assert _format_capacitance_for_netlist(1e-12) == "1e-12"
        assert _format_capacitance_for_netlist(10e-12) == "1e-11"
    
    def test_format_millifarad(self):
        """Test formatting values in millifarad range."""
        from capassigner.ui.plots import _format_capacitance_for_netlist
        assert _format_capacitance_for_netlist(2.2e-03) == "0.0022"
        assert _format_capacitance_for_netlist(1e-03) == "0.001"
    
    def test_format_farad(self):
        """Test formatting values in farad range."""
        from capassigner.ui.plots import _format_capacitance_for_netlist
        assert _format_capacitance_for_netlist(1.0) == "1"
        assert _format_capacitance_for_netlist(2.5) == "2.5"


class TestSPNodeConversion:
    """Test SPNode to lcapy netlist conversion."""
    
    def test_single_capacitor_netlist(self):
        """Test single capacitor produces correct netlist."""
        from capassigner.ui.plots import sp_to_lcapy_netlist
        
        node = Leaf(0, 1e-05)
        netlist = sp_to_lcapy_netlist(node, ["C1"], [1e-05])
        
        assert netlist == "C1 1 0 1e-05"
    
    def test_series_netlist(self):
        """Test series connection produces correct netlist."""
        from capassigner.ui.plots import sp_to_lcapy_netlist
        
        node = Series(Leaf(0, 1e-05), Leaf(1, 5e-06))
        netlist = sp_to_lcapy_netlist(node, ["C1", "C2"], [1e-05, 5e-06])
        
        lines = netlist.split("\n")
        assert len(lines) == 2
        assert "C1 1 2 1e-05" in lines
        assert "C2 2 0 5e-06" in lines
    
    def test_parallel_netlist(self):
        """Test parallel connection produces correct netlist."""
        from capassigner.ui.plots import sp_to_lcapy_netlist
        
        node = Parallel(Leaf(0, 1e-05), Leaf(1, 5e-06))
        netlist = sp_to_lcapy_netlist(node, ["C1", "C2"], [1e-05, 5e-06])
        
        lines = netlist.split("\n")
        assert len(lines) == 2
        assert "C1 1 0 1e-05" in lines
        assert "C2 1 0 5e-06" in lines
    
    def test_complex_netlist(self):
        """Test complex topology (Exercise 01 structure)."""
        from capassigner.ui.plots import sp_to_lcapy_netlist
        
        # Structure: Series(Parallel(C1, C2), Series(C3, C4))
        node = Series(
            Parallel(Leaf(0, 1e-05), Leaf(1, 5e-06)),
            Series(Leaf(2, 3e-06), Leaf(3, 7e-06))
        )
        netlist = sp_to_lcapy_netlist(
            node, 
            ["C1", "C2", "C3", "C4"], 
            [1e-05, 5e-06, 3e-06, 7e-06]
        )
        
        lines = netlist.split("\n")
        assert len(lines) == 4
        # C1 and C2 in parallel between nodes 1 and 2
        assert any("C1" in line and "1 2 1e-05" in line for line in lines)
        assert any("C2" in line and "1 2 5e-06" in line for line in lines)
        # C3 and C4 in series from node 2 to 0
        assert any("C3" in line and "2 3" in line for line in lines)
        assert any("C4" in line and "3 0" in line for line in lines)


class TestGraphConversion:
    """Test GraphTopology to lcapy netlist conversion."""
    
    def test_simple_graph_netlist(self):
        """Test simple graph A--B produces correct netlist."""
        from capassigner.ui.plots import graph_to_lcapy_netlist
        
        G = nx.MultiGraph()
        G.add_edge('A', 'B', capacitance=1e-05)
        topology = GraphTopology(G, 'A', 'B', [])
        
        netlist = graph_to_lcapy_netlist(topology)
        assert "CAB 1 0 1e-05" in netlist
    
    def test_graph_internal_node_netlist(self):
        """Test graph with internal node."""
        from capassigner.ui.plots import graph_to_lcapy_netlist
        
        G = nx.MultiGraph()
        G.add_edge('A', 'C', capacitance=1e-05)
        G.add_edge('C', 'B', capacitance=5e-06)
        topology = GraphTopology(G, 'A', 'B', ['C'])
        
        netlist = graph_to_lcapy_netlist(topology)
        lines = netlist.split("\n")
        
        assert len(lines) == 2
        assert any("CAC 1 2 1e-05" in line for line in lines)
        assert any("CCB 2 0 5e-06" in line for line in lines)
    
    def test_graph_parallel_edges_netlist(self):
        """Test graph with parallel edges (MultiGraph)."""
        from capassigner.ui.plots import graph_to_lcapy_netlist
        
        G = nx.MultiGraph()
        G.add_edge('A', 'B', capacitance=1e-05)
        G.add_edge('A', 'B', capacitance=5e-06)
        G.add_edge('A', 'B', capacitance=3e-06)
        topology = GraphTopology(G, 'A', 'B', [])
        
        netlist = graph_to_lcapy_netlist(topology)
        lines = netlist.split("\n")
        
        assert len(lines) == 3
        # Check unique labels
        assert any("CAB 1 0" in line for line in lines)
        assert any("CAB_1 1 0" in line for line in lines)
        assert any("CAB_2 1 0" in line for line in lines)


class TestLcapyRendering:
    """Test lcapy rendering integration."""
    
    def test_render_sp_circuit(self):
        """Test SP circuit rendering returns Figure."""
        from capassigner.ui.plots import render_sp_circuit
        
        node = Series(Leaf(0, 1e-05), Leaf(1, 5e-06))
        fig = render_sp_circuit(node, ["C1", "C2"], [1e-05, 5e-06])
        
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0
        
        plt.close(fig)
    
    def test_render_graph_network(self):
        """Test graph network rendering returns Figure."""
        from capassigner.ui.plots import render_graph_network
        
        G = nx.MultiGraph()
        G.add_edge('A', 'B', capacitance=1e-05)
        G.add_edge('A', 'B', capacitance=5e-06)
        topology = GraphTopology(G, 'A', 'B', [])
        
        fig = render_graph_network(topology)
        
        assert fig is not None
        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0
        
        plt.close(fig)

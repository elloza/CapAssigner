
import networkx as nx
import itertools

def generate_multigraphs(n_nodes, n_edges):
    """
    Generate all connected multigraphs with n_nodes and n_edges.
    Returns a list of nx.MultiGraph objects.
    """
    # Possible edges (pairs of nodes)
    nodes = range(n_nodes)
    possible_pairs = list(itertools.combinations(nodes, 2))
    # We can also have self-loops? Usually capacitors aren't self-loops.
    
    # Distribute n_edges into len(possible_pairs) bins.
    # This is combinations_with_replacement of pairs, length n_edges
    
    seen_hashes = set()
    unique_graphs = []
    
    for edges in itertools.combinations_with_replacement(possible_pairs, n_edges):
        G = nx.MultiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        
        if not nx.is_connected(G):
            continue
            
        # Isomorphism check
        # NetworkX Weisfeiler-Lehman hashing for multigraphs?
        # nx.weisfeiler_lehman_graph_hash is for labeled graphs usually, but works for structure
        # For multigraphs, we might need to be careful.
        # Simple check:
        is_new = True
        for existing_G in unique_graphs:
            if nx.is_isomorphic(G, existing_G):
                is_new = False
                break
        
        if is_new:
            unique_graphs.append(G)
            
    return unique_graphs

def sp_reduce(G_in, terminal_a, terminal_b):
    """
    Attempt to reduce G_in (MultiGraph) to a single edge between A and B.
    Returns the final graph.
    """
    G = G_in.copy()
    
    # We need to track edge attributes (capacitance). 
    # For this test, we just track structure.
    
    changed = True
    while changed:
        changed = False
        
        # 1. Parallel Reduction
        # Find pairs of nodes with > 1 edge
        # In NetworkX MultiGraph, G[u][v] gives a dictionary of edges.
        # We iterate over all node pairs that have edges.
        
        # We need to be careful modifying the graph while iterating.
        # Let's collect reductions first.
        
        # Parallel
        for u in list(G.nodes()):
            for v in list(G.neighbors(u)):
                if u >= v: continue # Check each pair once
                if G.number_of_edges(u, v) > 1:
                    # Found parallel edges
                    # print(f"Reducing parallel between {u} and {v}")
                    # Combine all edges into one
                    # In real app, sum capacitances
                    # Remove all edges, add one new edge
                    # For this structural test, just keep one edge? 
                    # No, we must remove k edges and add 1.
                    
                    # In a real reduction, we'd sum the values.
                    # Here we just simplify topology.
                    
                    # Remove all but one? No, remove all and add one new one to represent the combination.
                    # But for structural reduction check, having 1 edge is the goal.
                    # So we can just remove the extras.
                    
                    # Count edges
                    key_list = list(G[u][v].keys())
                    # Remove all but the first
                    for k in key_list[1:]:
                        G.remove_edge(u, v, key=k)
                    changed = True
        
        if changed: continue

        # 2. Series Reduction
        # Find node with degree 2, not A or B
        nodes = list(G.nodes())
        for n in nodes:
            if n == terminal_a or n == terminal_b:
                continue
            
            if G.degree(n) == 2:
                # Check if it has self loops? (Degree 2 could be one self loop)
                # Assuming simple paths for series.
                neighbors = list(G.neighbors(n))
                # If multigraph, neighbors might return same node twice if multiple edges?
                # nx.neighbors returns keys in dict, so unique neighbors.
                
                if len(neighbors) == 2:
                    u, v = neighbors
                    # Edges are (u, n) and (n, v)
                    # Remove n, add edge (u, v)
                    # print(f"Reducing series at {n}: {u}-{n}-{v}")
                    
                    # In real app, C_new = 1/(1/C1 + 1/C2)
                    G.remove_node(n)
                    G.add_edge(u, v)
                    changed = True
                    break # Restart loop
                elif len(neighbors) == 1:
                    # Self loop or double edge to same neighbor?
                    # If double edge to same neighbor, it's parallel (handled above)
                    # If self loop, it's irrelevant for SP usually?
                    pass
        
    return G

# Test
print("Generating graphs for E=4...")
graphs_4 = []
for v in range(2, 6): # V from 2 to 5
    gs = generate_multigraphs(v, 4)
    graphs_4.extend(gs)
    print(f"V={v}: {len(gs)} graphs")

print(f"Total graphs with 4 edges: {len(graphs_4)}")

# Test reduction on a known SP graph
# A-C1-C-C2-D-C3-B with C4 between C and D
# Nodes: A=0, B=1, C=2, D=3
# Edges: (0,2), (2,3), (3,1), (2,3)
G_sp = nx.MultiGraph()
G_sp.add_edge(0, 2) # C1
G_sp.add_edge(2, 3) # C2
G_sp.add_edge(3, 1) # C3
G_sp.add_edge(2, 3) # C4

print("Reducing example graph...")
G_reduced = sp_reduce(G_sp, 0, 1)
print(f"Reduced nodes: {G_reduced.nodes()}")
print(f"Reduced edges: {G_reduced.edges()}")
is_sp = (G_reduced.number_of_nodes() == 2 and G_reduced.number_of_edges() == 1)
print(f"Is SP reducible? {is_sp}")

# Test a bridge (Wheatstone)
# Nodes A, B, C, D.
# Edges: (A,C), (A,D), (C,B), (D,B), (C,D)
G_bridge = nx.MultiGraph()
G_bridge.add_edge(0, 2)
G_bridge.add_edge(0, 3)
G_bridge.add_edge(2, 1)
G_bridge.add_edge(3, 1)
G_bridge.add_edge(2, 3)

print("Reducing bridge graph...")
G_red_bridge = sp_reduce(G_bridge, 0, 1)
print(f"Reduced nodes: {G_red_bridge.nodes()}")
print(f"Reduced edges: {G_red_bridge.edges()}")
is_sp_bridge = (G_red_bridge.number_of_nodes() == 2 and G_red_bridge.number_of_edges() == 1)
print(f"Is SP reducible? {is_sp_bridge}")

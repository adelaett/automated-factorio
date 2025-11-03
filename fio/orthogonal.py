import networkx as nx
import numpy as np
from scipy.optimize import minimize
from collections import defaultdict

"""
Based on https://arxiv.org/abs/1807.09368
"""


def compact_layout(G, iters=None):
    """
    Compact orthogonal graph layout algorithm.
    G: networkx graph with node attributes 'w' and 'h' (width, height)
    Returns: G with updated 'x' and 'y' positions
    """
    n = len(G)
    c = compute_cell_size(G)  # grid cell size
    
    # Initialize grid positions and sizes
    for i, v in enumerate(G.nodes()):
        G.nodes[v]['x_grid'] = np.random.randint(0, int(5*np.sqrt(n)))
        G.nodes[v]['y_grid'] = np.random.randint(0, int(5*np.sqrt(n)))
        G.nodes[v]['w_grid'] = max(1, int(np.ceil(G.nodes[v].get('w', c) / c)))
        G.nodes[v]['h_grid'] = max(1, int(np.ceil(G.nodes[v].get('h', c) / c)))
    
    # Stage 1: Unit-sized nodes
    T = 2 * np.sqrt(n)
    k = (0.2 / T) ** (1 / (90 * np.sqrt(n)))
    if iters is None:
        iters = int(45 * np.sqrt(n))
    
    for it in range(iters):
        print(it/iters)
        for v in G.nodes():
            # Move node to median neighbor position + random offset
            neighbors = list(G.neighbors(v))
            if neighbors:
                med_x = np.median([G.nodes[u]['x_grid'] for u in neighbors])
                med_y = np.median([G.nodes[u]['y_grid'] for u in neighbors])
                target_x = med_x + np.random.uniform(-T, T)
                target_y = med_y + np.random.uniform(-T, T)
                
                move_node(G, v, target_x, target_y)
            
            # Try swapping with adjacent nodes
            swap_with_neighbors(G, v)
        
        # Compaction every 9 iterations
        if it % 9 == 8:
            compact(G, horizontal=(it % 18 == 0), gamma=3.0)
        
        T *= k
    
    # Stage 2: Real-sized nodes
    compact(G, horizontal=True, gamma=3.0, expand=True)
    compact(G, horizontal=False, gamma=3.0, expand=True)
    
    for it in range(iters, 2*iters):
        print(it/iters)
        for v in G.nodes():
            neighbors = list(G.neighbors(v))
            if neighbors:
                w_g, h_g = G.nodes[v]['w_grid'], G.nodes[v]['h_grid']
                med_x = np.median([G.nodes[u]['x_grid'] for u in neighbors])
                med_y = np.median([G.nodes[u]['y_grid'] for u in neighbors])
                target_x = med_x + np.random.uniform(-T*w_g, T*w_g)
                target_y = med_y + np.random.uniform(-T*h_g, T*h_g)
                
                move_node(G, v, target_x, target_y)
            
            swap_with_neighbors(G, v)
        
        if it % 9 == 0:
            gamma = max(1.0, 1 + 2*(2*iters - it - 30)/(0.5*2*iters))
            compact(G, horizontal=(it % 18 == 0), gamma=gamma)
        
        T *= k
    
    # Convert to real coordinates
    for v in G.nodes():
        G.nodes[v]['x'] = G.nodes[v]['x_grid'] * c
        G.nodes[v]['y'] = G.nodes[v]['y_grid'] * c
    
    return G


def compute_cell_size(G):
    """Compute grid cell size based on node dimensions."""
    widths = [G.nodes[v].get('w', 10) for v in G.nodes()]
    heights = [G.nodes[v].get('h', 10) for v in G.nodes()]
    L_min = min(min(widths), min(heights))
    L_max = max(max(widths), max(heights))
    
    if L_max < 3*L_min:
        return L_max
    elif L_max < 15*L_min:
        return 3*L_min/2
    else:
        return L_max/30


def move_node(G, v, target_x, target_y):
    """Move node v to best free position near (target_x, target_y)."""
    grid = build_grid(G)
    w_g, h_g = G.nodes[v]['w_grid'], G.nodes[v]['h_grid']
    
    # Remove node from current position
    x_old, y_old = G.nodes[v]['x_grid'], G.nodes[v]['y_grid']
    for dx in range(w_g):
        for dy in range(h_g):
            grid.pop((x_old + dx, y_old + dy), None)
    
    # Find best nearby position
    best_pos, best_score = None, float('inf')
    search_radius = int(abs(target_x - x_old) + abs(target_y - y_old)) + 2
    
    for x in range(int(target_x - search_radius), int(target_x + search_radius + 1)):
        for y in range(int(target_y - search_radius), int(target_y + search_radius + 1)):
            if is_free(grid, x, y, w_g, h_g):
                score = total_edge_length(G, v, x, y)
                if score < best_score:
                    best_score = score
                    best_pos = (x, y)
    
    if best_pos:
        G.nodes[v]['x_grid'], G.nodes[v]['y_grid'] = best_pos


def swap_with_neighbors(G, v):
    """Try swapping node v with adjacent nodes if beneficial."""
    grid = build_grid(G)
    x, y = G.nodes[v]['x_grid'], G.nodes[v]['y_grid']
    w_v, h_v = G.nodes[v]['w_grid'], G.nodes[v]['h_grid']
    
    # Check adjacent cells
    for u in G.nodes():
        if u == v:
            continue
        x_u, y_u = G.nodes[u]['x_grid'], G.nodes[u]['y_grid']
        w_u, h_u = G.nodes[u]['w_grid'], G.nodes[u]['h_grid']
        
        # Check if adjacent and swappable
        if abs(x - x_u) <= max(w_v, w_u) and abs(y - y_u) <= max(h_v, h_u):
            if w_v == w_u and h_v == h_u:  # Only swap same-sized nodes
                gain = (total_edge_length(G, v, x, y) + total_edge_length(G, u, x_u, y_u) -
                        total_edge_length(G, v, x_u, y_u) - total_edge_length(G, u, x, y))
                if gain > 0:
                    G.nodes[v]['x_grid'], G.nodes[v]['y_grid'] = x_u, y_u
                    G.nodes[u]['x_grid'], G.nodes[u]['y_grid'] = x, y
                    return


def compact(G, horizontal=True, gamma=1.0, expand=False):
    """Perform quadratic compaction in one direction."""
    nodes = list(G.nodes())
    n = len(nodes)
    
    # Build visibility graph
    vis_edges = build_visibility_graph(G, horizontal)
    
    # Setup quadratic program: min sum((z_i + w_i/2 - z_j - w_j/2)^2)
    # subject to: z_j - z_i >= gamma * w_i for each visibility edge (i,j)
    
    def objective(z):
        cost = 0
        for u, v in G.edges():
            i, j = nodes.index(u), nodes.index(v)
            w_i = G.nodes[u]['w_grid'] if horizontal else G.nodes[u]['h_grid']
            w_j = G.nodes[v]['w_grid'] if horizontal else G.nodes[v]['h_grid']
            diff = z[i] + w_i/2 - z[j] - w_j/2
            cost += diff**2
        return cost
    
    # Constraints: z_j - z_i >= gamma * w_i
    constraints = []
    for i, j in vis_edges:
        w_i = G.nodes[nodes[i]]['w_grid'] if horizontal else G.nodes[nodes[i]]['h_grid']
        constraints.append({
            'type': 'ineq',
            'fun': lambda z, i=i, j=j, d=gamma*w_i: z[j] - z[i] - d
        })
    
    # Initial positions
    z0 = np.array([G.nodes[v]['x_grid'] if horizontal else G.nodes[v]['y_grid'] 
                   for v in nodes])
    
    # Solve
    result = minimize(objective, z0, constraints=constraints, method='SLSQP')
    
    # Update positions
    for i, v in enumerate(nodes):
        if expand:
            if horizontal:
                G.nodes[v]['w_grid'] = max(1, int(np.ceil(G.nodes[v].get('w', 10) / compute_cell_size(G))))
            else:
                G.nodes[v]['h_grid'] = max(1, int(np.ceil(G.nodes[v].get('h', 10) / compute_cell_size(G))))
        
        if horizontal:
            G.nodes[v]['x_grid'] = int(np.floor(result.x[i]))
        else:
            G.nodes[v]['y_grid'] = int(np.floor(result.x[i]))


def build_visibility_graph(G, horizontal):
    """Build visibility graph for compaction constraints."""
    grid = build_grid(G)
    nodes = list(G.nodes())
    vis_edges = []
    
    for i, u in enumerate(nodes):
        x_u, y_u = G.nodes[u]['x_grid'], G.nodes[u]['y_grid']
        for j, v in enumerate(nodes):
            if i >= j:
                continue
            x_v, y_v = G.nodes[v]['x_grid'], G.nodes[v]['y_grid']
            
            if horizontal and x_v > x_u:
                if can_connect_horizontal(grid, u, v, G):
                    vis_edges.append((i, j))
            elif not horizontal and y_v > y_u:
                if can_connect_vertical(grid, u, v, G):
                    vis_edges.append((i, j))
    
    return vis_edges


def build_grid(G):
    """Build grid dict: {(x,y): node_id}"""
    grid = {}
    for v in G.nodes():
        x, y = G.nodes[v]['x_grid'], G.nodes[v]['y_grid']
        w_g, h_g = G.nodes[v]['w_grid'], G.nodes[v]['h_grid']
        for dx in range(w_g):
            for dy in range(h_g):
                grid[(x + dx, y + dy)] = v
    return grid


def is_free(grid, x, y, w, h):
    """Check if rectangle is free in grid."""
    for dx in range(w):
        for dy in range(h):
            if (x + dx, y + dy) in grid:
                return False
    return True


def total_edge_length(G, v, x, y):
    """Calculate total edge length if node v placed at (x,y)."""
    total = 0
    for u in G.neighbors(v):
        x_u, y_u = G.nodes[u]['x_grid'], G.nodes[u]['y_grid']
        total += np.sqrt((x - x_u)**2 + (y - y_u)**2)
    return total


def can_connect_horizontal(grid, u, v, G):
    """Check if horizontal line can connect u and v without obstacles."""
    x_u, y_u = G.nodes[u]['x_grid'], G.nodes[u]['y_grid']
    x_v, y_v = G.nodes[v]['x_grid'], G.nodes[v]['y_grid']
    # Simplified: just check if y-ranges overlap
    h_u, h_v = G.nodes[u]['h_grid'], G.nodes[v]['h_grid']
    return not (y_u + h_u < y_v or y_v + h_v < y_u)


def can_connect_vertical(grid, u, v, G):
    """Check if vertical line can connect u and v without obstacles."""
    x_u, y_u = G.nodes[u]['x_grid'], G.nodes[u]['y_grid']
    x_v, y_v = G.nodes[v]['x_grid'], G.nodes[v]['y_grid']
    w_u, w_v = G.nodes[u]['w_grid'], G.nodes[v]['w_grid']
    return not (x_u + w_u < x_v or x_v + w_v < x_u)

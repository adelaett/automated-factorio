import networkx as nx
import mip
from typing import List, Any, Iterable, Tuple
import random
from collections import deque

def continuous_pairs(it: Iterable[Any], k=2) -> Iterable[Tuple[Any]]:
    it = iter(it)
    q = deque(maxlen=k)
    try:
        for _ in range(k):
            q.append(next(it))

        yield tuple(q)
        while True:
            q.append(next(it))
            yield tuple(q)
    except StopIteration:
        return None


def kou_markowsky(G: nx.Graph, T: List[Any], weight: str):
    assert nx.is_connected(G)
    assert all(u in G.nodes() for u in T)

    H = nx.Graph()
    H.add_nodes_from(G)
    for u, d in nx.all_pairs_dijkstra_path(G, weight=weight):
        for v, p in d.items():
            H.add_edge(u, v, path=p, weight=nx.path_weight(G, p, weight))

    M = nx.minimum_spanning_tree(nx.induced_subgraph(H, T), weight=weight)

    S = nx.Graph()
    for u, v, d in M.edges(data=True):
        for x in d['path']:
            S.add_node(x, **G.nodes[x])
        for x, y in continuous_pairs(d['path']):
            S.add_edge(x, y, **G.edges[x, y])

    return S




def place(graph: nx.DiGraph):
    m = mip.Model(sense=mip.MAXIMIZE)

    x = dict()
    y = dict()
    for u in graph.edges(data=True):
        x[u] = m.add_var(name=f"x_{u}", lb=0, up=100, var_type=mip.INTEGER)
        y[u] = m.add_var(name=f"y_{u}", lb=0, up=100, var_type=mip.INTEGER)


    for u, v, info in graph.edges(data=True):
        assert False

if __name__ == "__main__":
    G = nx.random_internet_as_graph(1000)

    for u, v in G.edges():
        G.edges[u, v]["weight"] = random.random()

    T = random.choices(list(G.nodes()), k=20)

    print(kou_markowsky(G, T, "weight"))

import numpy as np

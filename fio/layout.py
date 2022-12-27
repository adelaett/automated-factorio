import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, PathPatch, FancyArrowPatch
from matplotlib.path import Path
import numpy as np
import json
from itertools import count
import requests


def filter_serializing(info):
    data = {}

    for k, v in info.items():
        if type(k) != str:
            continue

        if k == "id":
            continue

        try:
            json.dumps(v)
        except TypeError:
            continue

        data[k] = v
    
    return data

def to_nested(params):
    parameters = {}
    for k, v in params.items():
        x = parameters
        path = k.split("/")
        for i in path[:-1]:
            if i not in x:
                x[i] = {}
            x = x[i]
        x[path[-1]] = v
    
    return parameters

def read_pos(t):
    return t["x"], t["y"]

def get_layout(graph, params=None):
    if params is None:
        params = {}
    params = to_nested(params)

    children = []
    for node, info in graph.nodes(data=True):
        if "width" not in info:
            info["width"] = 100
        if "height" not in info:
            info["height"] = 100
        children.append(dict(id=node, **filter_serializing(info)))
    
    c = count()
    edges = [{"id": next(c), "source": u, "target": v} for u, v in graph.edges]
    
    request =  dict({
        "id": "root",
        "children": children,
        "edges": edges,
    }, **params)
    
    print(f"request length : {len(json.dumps(request, indent=False))}")

    response = requests.post("http://0.0.0.0:7070/layout", json=request)
    if response.status_code != 200:
        print(response.text)
        raise AssertionError()
    response = response.json()
    
    for node in response["children"]:
        for k, v in node.items():
            if k in ["id"]:
                continue
            if k not in graph.nodes[node["id"]]:
                graph.nodes[node["id"]][k] = v

    for edge in response["edges"]:
        polylines = []
        for s in edge["sections"]:
            polylines.append([read_pos(p) for p in [s["startPoint"]] + (s["bendPoints"] if "bendPoints" in s else []) + [s["endPoint"]]])
            
        for k, v in edge.items():
            if k in ["id", "source", "sources", "target", "targets"]:
                continue
            if k not in graph.edges[edge["source"], edge["target"]]:
                graph.edges[edge["source"], edge["target"]][k] = v

        graph.edges[edge["source"], edge["target"]]["polylines"] = polylines
    
    return graph

def read_pos(t):
    return t["x"], t["y"]

def make_rect(node):
    u, info = node
    
    if info["kind"] == "exchange":
        return Rectangle(read_pos(info), width=info["width"] or 10, height=info["height"] or 10)
    else:
        return Rectangle(read_pos(info), width=info["width"] or 10, height=info["height"] or 10)


def make_graph(ax, layout):
    nodes_patches = [make_rect(node) for node in layout.nodes(data=True)]
    pc1 = PatchCollection(nodes_patches, facecolor=None, edgecolor="white")
    
    edges_patches = [FancyArrowPatch(path=Path(list((c["polylines"][0])), closed=False), fill=False, arrowstyle="->") for _, _, c in layout.edges(data=True)]
    pc2 = PatchCollection(edges_patches, facecolor="none", edgecolor="white")
    
    ax.add_collection(pc1)
    ax.add_collection(pc2)

def plot_layout(graph, params=None):

    layout =  get_layout(graph, params)
    
    fig, ax = plt.subplots(1, figsize=(40, 40))

    make_graph(ax, layout)

    xs = [x for _, x in layout.nodes(data="x")]
    ys = [y for _, y in layout.nodes(data="y")]

    plt.xlim((min(xs)-500, max(xs)+500))
    plt.ylim((min(ys)-500, max(ys)+500))



    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high)))

    from datetime import datetime

    dt = datetime.now()
    return plt.savefig(f"figures/layout-{dt.strftime(r'layout-%Y-%m-%d_%H-%M-%S')}.png")

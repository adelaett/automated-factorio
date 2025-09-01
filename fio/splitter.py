from . import blueprint
from . import arith


# Generated using hand-made factorio blueprint book
book = blueprint.loads("""0eNrNW02Po0YQ/SsrzvaK/qA/fMslt5xyjCILzzCzKBgsDKOMVv7vabBFe9dgV9V070RaaWXGflRX1XtdVTTfk13VF4e2rLvtrmn+STbf/ZVjsvnr6uPwt/Kpqc+Xj+VrnVfDte79UCSbpOyKfbJK6nw/fOravD4emrZb74qqS06rpKyfi3+TDTv9vUqKuiu7sjgjjR/et3W/3xWt+8KEMdyry+tu/dTsd2Wdd03rbnBoju63TT3c2uFZ+TVbJe/JRuivmbvNc9kWT+e/89UA0bVNtd0V3/K30v3e/eilrLqiBa3iuRhtaPsRcX2o8rp2Np4G4H7wCLte1+m0ulkNR65GXFYj2bgatP1vZdv17sp02/M31r9hjBZLYVz2/sXea+/PAEtibGX2+bF1aTsCbK4YsUqq3DlmwK4P/fD5zd39bKBhUluuM+X+SeMJkA5+gZJqKZwpjVGPwqnZxeFMQsLJ4cAcBQxPQC1QwJLgCgMBzggW25+B5Qyw8qE/VGXnsvued+1jSzXBUpALDN63HKQalgCcQnzLUoxzOb+RoLPcLIvJKmn6zgnD1nG9ad2t3Ver4mXYD2+NYXg23S5TzSFzfMiByIIQGg6JOZMEm2eQ76v2UwqSbBZCstmVZPNwkq2ySJLtgbOwkq00UbKXOarUZGsQjrbl67dZkmYE9znbTkRh9+syIYXdR0DP2waXcm+hggiGJdgIAr6ScnhkQNsaQpe9zTBkAhmB6klgY3BdnlKDoMsMpMsco8s/Vv8T535SeVIFHlDOtYlVgdtIFbhhkSpwk6KA4dJscM2IIvgYxH9NALaBK3GDstgSgEEWgypxn2k2qGz7RLOBZdsjm8Cy7XPYBJZtjwzqT5nnXe/UsH1tG/f/o6y4tBcXjT0XYLNNkcL7Gtj7abzCAZsig8nl2F2lJTgQ1JXzFJ9SMAdyhhdGLiBB5xwvYLC6iAsSDcQ1Dc4zxDlwSXAIzOyMwAIBCiKFuTBkTUCGecMQUhpmsyUgg2wWKSE3JMRmQahaR+QHxf0eNnTRn1jcR5rVmFizGiNjFfcqVnGvUNOlDLKl6l80BEIoG66b04SAK1xD8Hhz8tAaVqNZQv5rZFMAR1ag4o8RElWHbg6QEy6B4oAJ2xSoB9NMlhFIAVs3hW4Lc01GYRiswTKEXIUhWxJ5LayyTAkpADIbUcQb3BDiqohHOOTS1DxUMy7wKTK2NR+r26ekADYyGQEZVgMrkneBjQyBf+FLd9zEG1O6a1RTIAjkAyIT9jdgu8HxtAbaLAjIMJslIevkPKUFhXgz7daDFgn2/MPQW6Q75/P+B09BbKxGycZqlGysRslK4jmk5SLRe9eGfPrhXQAaHGsCMPIcEsAFkcevFp/ywCFzis8g2FwX0RtZiRu5c3zIg59DshK1KyF6JJvhkDOCzbBn9ATOApEJpJ3zxv3drwWeyhKfvv1FmhPalLj93RE89ouGY4KwyizwlskjHRzwFn/gTJePRNAzXR4WNFUxBG8GPuHlgZemNSkhMqHPdFke60yXxT1Qw+xx0c7aWtwDNUbgFtAbCh9BILImIKNPuLWwDo9J+h73kh+7dYj3sMBjD6Fw2xXoJSBjf0QP9koUi/NK1DScgHlD4t0s08Dn4cziS1wyzOMvmeI6QsDkcYK+nZc+nkMawhI4ZAmEWeHtu20f7Pc8skTuhTg+XuCD8THF8JFxUrJky8ly5xAagfxA31PYH/AJnFTY3uziJdDelc1hrcfXjD3gH81zX+Xtl9/bfDTBZcKXP33xPFx8K7YT5J0bn/4DwGDrDQ==""")
book = {b["blueprint"]["label"]: blueprint.clean(b["blueprint"]["entities"]) for b in book["blueprint_book"]["blueprints"]}


def sequence_from_frac(f):
    const, rep = arith.frac_to_ver(f)

    l: list[str] = []

    l.append("input")

    for c in const:
        l.append(f"c{c}")

    if len(rep) == 0:
        l.append("m0")
    else:
        rep = iter(rep)
        l.append(f"m{next(rep)}")
        for r in rep:
            l.append(f"r{r}")

    l.append("output")

    return l

def entitites_from_frac(f):
    delta_x = 0
    entities = []
    for label in sequence_from_frac(f):
        entities.extend(blueprint.translate(delta_x, 0, book[label]))
        delta_x += blueprint.size(book[label])[0]
    ents = blueprint.recount(entities)

    input_ = None
    output1 = None
    output0 = None

    to_remove = []

    for e in ents:
        if e["name"] == "constant-combinator":
            if e["control_behavior"]["filters"][0]["signal"]["name"] == "signal-A":
                input_ = e["position"]
                to_remove.append(e["entity_number"])
            elif e["control_behavior"]["filters"][0]["signal"]["name"] == "signal-1":
                output1 = e["position"]
                to_remove.append(e["entity_number"])
            elif e["control_behavior"]["filters"][0]["signal"]["name"] == "signal-0":
                output0 = e["position"]
                to_remove.append(e["entity_number"])

    ents = [e for e in ents if e["entity_number"] not in to_remove]
    ents = blueprint.recount(ents)

    ports = {
        "input": input_,
        "output1": output1,
        "output0": output0
    }

    return {
        "ports": ports,
        "entities": entities,
        "size": blueprint.size(entities)
    }



def horner_splitter(g, c, top, bot, cur, t):
    for x in t:
        splitter = next(c); g.add_node(splitter, kind="splitter")
        last = cur
        cur = next(c); g.add_node(cur, kind="wire")

        leave = next(c); g.add_node(leave, kind="wire")

        g.add_edge(last, splitter)
        g.add_edge(splitter, cur)
        
        merger = next(c); g.add_node(merger, kind="splitter")
        if x == 1:
            last_top = top
            top = next(c); g.add_node(top, kind="wire")
            
            g.add_edge(last_top, merger)
            g.add_edge(merger, top)
        elif x == 0:
            last_bot = bot
            bot = next(c); g.add_node(bot, kind="wire")
            
            g.add_edge(last_bot, merger)
            g.add_edge(merger, bot)
        
        g.add_edge(splitter, leave)
        g.add_edge(leave, merger)
    
    return top, bot, cur


def fractionnal_splitter(p, q=None, c=None):
    t, r = frac_to_ver(p, q)
    
    # terminating part
    # putting mergers and splitters using the microservice
    if c is None:
        c = count()
    g = nx.DiGraph()
    
    top = next(c); g.add_node(top, kind="wire", info="top_in")
    bot = next(c); g.add_node(bot, kind="wire", info="bot_in")
    in_ = next(c); g.add_node(in_, kind="wire", info="input")

    top, bot, partial_out = horner_splitter(g, c, top, bot, in_, t)
    
    if len(r) == 0:
        # merge partial_out with bot, this will be the bot output
        
        top_out = top
        g.nodes[top_out]["info"] = "top_out"
        
        bot_out = next(c); g.add_node(bot_out, kind="wire", info="bot_out")
        merger = next(c); g.add_node(merger, kind="splitter")
        g.add_edge(partial_out, merger)
        g.add_edge(bot, merger)
        g.add_edge(merger, bot_out)
    else:
        cur = next(c); g.add_node(cur, kind="wire")
        merger = next(c); g.add_node(merger, kind="splitter")
        
        top_out, bot_out, final = horner_splitter(g, c, top, bot, cur, r)
        g.add_edge(partial_out, merger)
        g.add_edge(merger, cur)
        g.add_edge(final, merger)
        
        g.nodes[top_out]["info"] = "top_out"
        g.nodes[bot_out]["info"] = "bot_out"
        
    assert nx.is_bipartite(g)
    h = g.copy()
    for n, info in g.nodes(data=True):
        if info["kind"] == "wire" and (len(g.in_edges(n)), len(g.out_edges(n))) != (1, 1):
            assert "info" in info
        
        elif info["kind"] == "wire" and (len(g.in_edges(n)), len(g.out_edges(n))) == (1, 1):
            from_ =  next(iter(g.in_edges(n)))[0]
            to = next(iter(g.out_edges(n)))[1]
            
            h.add_edge(from_, to)
            h.remove_node(n)

    return h, in_, top_out, bot_out


def gen_tree(tree, in_, outputs, c=None):
    if c is None:
        c = count()
    if tree.left is None and tree.right is None:
        # finished
        outputs[tree.info] = in_
        return nx.DiGraph()
    else:
        g3, in_splitter, top_out, bot_out = fractionnal_splitter(tree.right.v / tree.v, c=c)

        g1 = gen_tree(tree.right, top_out, outputs, c)
        g2 = gen_tree(tree.left, bot_out, outputs, c)
        
        g = nx.compose_all([g1, g2, g3])
        
        g.add_edge(in_, in_splitter, ratio_here=tree.v)

        return g


def generate_splitter(A):
    tree = get_splitter_tree(A)
    
    c = count()
    outputs = {}
    in_ = next(c)
    
    g = gen_tree(tree, in_, outputs, c)
    
    g.nodes[in_]["kind"] = "wire"
    
    for n in g.nodes:
        if g.nodes[n]["kind"] == "wire":
            g.nodes[n]["width"] = 10
            g.nodes[n]["height"] = 10
            g.nodes[n]["size"] = 10
        elif g.nodes[n]["kind"] == "splitter":
            g.nodes[n]["width"] = 10
            g.nodes[n]["height"] = 20

    for k, n in outputs.items():
        g.nodes[n]["width"] = 40
        g.nodes[n]["height"] = 10
    
    g.nodes[in_]["width"] = 40
    g.nodes[in_]["height"] = 10
    
    return g


import copy

import blueprint
import arith
import networkx as nx
from fractions import Fraction as F
from itertools import count

def add_edge_port(graph, n1, n2, data=None):
    if data is None:
        data = {}
    n1, p1 = n1.split(".")
    n2, p2 = n2.split(".")
    graph.add_edge(n1, n2, p1=p1, p2=p2, **data)

def gen_tree(graph, tree, in_, out_names, c=None):
    if c is None:
        c = count()
    if tree.left is None and tree.right is None:
        # tree is a leaf
        add_edge_port(graph, in_, out_names[tree.info])
        return nx.DiGraph()
    else:
        data = entitites_from_frac(tree.right.v / tree.v)
        data = {}

        n = next(c)
        graph.add_node(f"node-{n}", **data)
        add_edge_port(graph, in_, f"node-{n}.input")
        gen_tree(graph, tree.right, f"node-{n}.output-1", out_names, c=c)
        gen_tree(graph, tree.left, f"node-{n}.output-0", out_names, c=c)

def build_graph(A, in_, out_names, graph=None, c=None):
    tree = arith.get_splitter_tree(A)

    if c is None:
        c = count()
    if graph is None:
        graph = nx.DiGraph()

    # we assume that the outputs and the input are already in the graph
    assert in_.split(".")[0] in graph.nodes()
    assert all(out.split(".")[0] in graph.nodes() for out in out_names)

    gen_tree(graph, tree, in_, out_names, c)

    return graph

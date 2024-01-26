import mip
import networkx as nx
import math
import fio.arith as arith

def compute_cost(data):
    return 1 # data["machine"]["energy_usage"]

def ingredients_coefs(r, m):
    return {
        i["name"]: m["crafting_speed"] * i["amount"]/ r["energy"]
        for i in r["ingredients"]
    }

def products_coefs(r, m):
    print(r["products"])
    return {
        p["name"]: m["crafting_speed"] * (p["amount"] if "amount" in p else (p["amount_min"] + p["amount_min"] / 2) * p["probability"])/r["energy"]
        for p in r["products"]
    }

def ingredient_coef(data, v):
    coef = data["machine"]["crafting_speed"] * sum(i["amount"] for i in data["recipe"]["ingredients"] if i["name"] == v) / data["recipe"]["energy"]
    assert coef > 0
    return coef

def product_coef(data, v):
    try:
        coef = data["machine"]["crafting_speed"] * sum(p["amount"] for p in data["recipe"]["products"] if p["name"] == v) / data["recipe"]["energy"]
    except:
        coef = data["machine"]["crafting_speed"] * sum((p["amount_min"] + p["amount_max"])/2*p["probability"] for p in data["recipe"]["products"] if p["name"] == v) / data["recipe"]["energy"]
    
    assert coef >= 0
    return coef

def optimize_model(graph, sources):
    model = mip.Model()
    model.verbose = 0

    flow_int = {data["name"]: model.add_var(f"flow_{data['name']}", lb=0, obj=compute_cost(data), var_type=mip.INTEGER) for a, b, data in graph.edges_data()}
    flow = {data["name"]: model.add_var(f"flow_{data['name']}", lb=0, obj=compute_cost(data)) for a, b, data in graph.edges_data()}
    
    for _, _, d in graph.edges_data():
        model.add_constr(flow[d["name"]] <= flow_int[d["name"]])
    
    diffs = {}
    produced = {}
    used = {}
    
    considered = {}

    for v in graph.nodes():
        
        diff = mip.quicksum(flow[data["name"]] * ingredient_coef(data, v) for (_, _, data) in graph.out_edges_data(v)) - mip.quicksum(flow[data["name"]] * product_coef(data, v) for (_, _, data) in graph.in_edges_data(v))
        diffs[v] = diff 
        
        considered[v] = mip.quicksum(flow[data["name"]] * ingredient_coef(data, v) for (_, _, data) in graph.out_edges_data(v)) + mip.quicksum(flow[data["name"]] * product_coef(data, v) for (_, _, data) in graph.in_edges_data(v))

        for (_, _, data) in graph.in_edges_data(v):
            produced[v, data["name"]] = flow[data["name"]] * product_coef(data, v)

        for (_, _, data) in graph.out_edges_data(v):
            used[v, data["name"]] = flow[data["name"]] * ingredient_coef(data, v)

        # model.objective = model.objective - diff


        if v in sources:
            model.add_constr(diff <= sources[v])
        else:
            model.add_constr(diff <= 0)

    model.optimize(max_seconds=1)
    if model.status in [mip.OptimizationStatus.FEASIBLE, mip.OptimizationStatus.OPTIMAL]:
        return {
            "kind": "solution",
            "status": model.status,
            # "diffs": {k: (v.x) for k, v in diffs.items() if round(v.x, 3) != 0},
            # "considered": {k for k, v in considered.items() if round(v.x, 3) != 0},
            # "used": {k: (v.x) for k, v in used.items() if round(v.x, 3) != 0},
            # "produced": {k: (v.x) for k, v in produced.items() if round(v.x, 3) != 0},
            "flow": {k: (math.ceil(v.x), (v.x)) for k, v in flow.items() if v.x is not None and round(v.x, 3) > 0},
        }
    else:
        return {
            "kind": "none",
            "status": model.status
        }



def build_detailed_graph(model):
    """depreciated"""
    result = model

    assert result["kind"] == "solution"

    layout = nx.DiGraph()

    for u in result["considered"]:
        layout.add_node(u, kind="exchange", Text="u")

    for u, w in result["flow_int"].items():
        layout.add_node(u, kind="sub-factory", amount=w, Text="u")

    for (u, v), w in result["used"].items():
        layout.add_edge(u, v, flow=w)

    for (u, v), w in result["produced"].items():
        layout.add_edge(v, u, flow=w)

    for u, info in layout.nodes(data=True):
        if info["kind"] == "exchange":
            size = math.ceil(math.sqrt(max(sum(math.ceil(f/15) for u, v, f in layout.out_edges(u, data="flow")),
                       sum(math.ceil(f/15) for u, v, f in layout.in_edges(u, data="flow"))) * 5))

            layout.nodes[u]["label"] = f"exchange: {u}"

            layout.nodes[u]['graphics'] = {"w": size, "h": size}
            layout.nodes[u]["in__flow"] = sum(f for u, v, f in layout.in_edges(u, data="flow"))
            layout.nodes[u]["out_flow"] = sum(f for u, v, f in layout.out_edges(u, data="flow"))
        elif info["kind"] == "sub-factory":
            size = math.ceil(math.sqrt(info["amount"])) * 5

            layout.nodes[u]["label"] = f"exchange: {u}"
            layout.nodes[u]['graphics'] = {"w": size, "h": size}

        else:
            assert False
    
    return layout

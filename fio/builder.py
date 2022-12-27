import mip

class HyperDiGraph:
    def __init__(self):
        self._edges = []
        self._nodes = set()

    def add_edge(self, A, B, data=None):
        self._edges.append((A, B, data))
        self._nodes.update(A)
        self._nodes.update(B)
    
    def in_edges(self, v):
        assert v in self._nodes
        return [(e[0], e[1]) for e in self._edges if v in e[1]]

    def in_edges_data(self, v):
        assert v in self._nodes
        return [e for e in self._edges if v in e[1]]

    def out_edges(self, v):
        assert v in self._nodes
        return [(e[0], e[1]) for e in self._edges if v in e[0]]

    def out_edges_data(self, v):
        assert v in self._nodes
        return [e for e in self._edges if v in e[0]]

    def edges(self):
        return [(e[0], e[1]) for e in self._edges]

    def edges_data(self):
        return [e for e in self._edges]

    def nodes(self):
        return [v for v in self._nodes]
    
    def edge_by_name(self, name):
        return next(d for (_, _, d) in self._edges if d["name"] == name)


def compute_cost(data):
    return 1 # data["machine"]["energy_usage"]

def ingredient_coef(data, v):
    coef = data["machine"]["crafting_speed"] * sum(i["amount"] for i in data["recipe"]["ingredients"] if i["name"] == v) / data["recipe"]["energy"]
    assert coef > 0
    return coef

def product_coef(data, v):
    try:
        coef = data["machine"]["crafting_speed"] * sum(p["amount"]*p["probability"] for p in data["recipe"]["products"] if p["name"] == v) / data["recipe"]["energy"]
    except:
        coef = data["machine"]["crafting_speed"] * sum((p["amount_min"] + p["amount_max"])/2*p["probability"] for p in data["recipe"]["products"] if p["name"] == v) / data["recipe"]["energy"]
    assert coef > 0
    return coef

class namespace(dict):
    def __getattr__(self, k):
        return self[k]

class Solver:
    def __init__(self, graph):
        self.graph = graph
    
    def build_model(self, sources):
        model = mip.Model()

        flow_int = {
            data["name"]: model.add_var(f"flow_{data['name']}", lb=0, obj=compute_cost(data), var_type=mip.INTEGER)
            for a, b, data in self.graph.edges_data()
        }
        flow = {
            data["name"]: model.add_var(f"flow_{data['name']}", lb=0, obj=compute_cost(data))
            for a, b, data in self.graph.edges_data()
        }
        
        for _, _, d in self.graph.edges_data():
            model.add_constr(flow[d["name"]] <= flow_int[d["name"]])

        diffs = {}    
        produced = {}
        used = {}
        
        considered = {}
        
        fluids = {} # {f["name"] for f in db.fluid.find({})}

        for v in self.graph.nodes():
            
            diff = \
                  mip.quicksum(flow[data["name"]] * ingredient_coef(data, v) for (_, _, data) in self.graph.out_edges_data(v)) \
                - mip.quicksum(flow[data["name"]] * product_coef(data, v) for (_, _, data) in self.graph.in_edges_data(v))

            diffs[v] = diff
            
            considered[v] = \
                  mip.quicksum(flow[data["name"]] * ingredient_coef(data, v) for (_, _, data) in self.graph.out_edges_data(v)) \
                + mip.quicksum(flow[data["name"]] * product_coef(data, v) for (_, _, data) in self.graph.in_edges_data(v))
            
            for (_, _, data) in self.graph.in_edges_data(v):
                used[v, data["name"]] = flow[data["name"]] * product_coef(data, v)
            
            for (_, _, data) in self.graph.out_edges_data(v):
                produced[v, data["name"]] = flow[data["name"]] * ingredient_coef(data, v)
            
            # model.objective = model.objective - diff
            
            if v in sources:
                model.add_constr(diff <= sources[v])
            elif v in fluids:
                model.add_constr(diff == 0)
            else:
                model.add_constr(diff <= 0)

        model.optimize()

        return namespace({
            "diffs": {k: v.x for k, v in diffs.items() if v.x is not None and v.x != 0},
            "considered": {k for k, v in considered.items() if v.x is not None and v.x != 0},
            "used": {k: v.x for k, v in used.items() if v.x is not None and v.x != 0},
            "produced": {k: v.x for k, v in produced.items() if v.x is not None and v.x != 0},
            "config": {k: v.x for k, v in flow.items() if v.x is not None and v.x > 0},
            "config_int": {k: v.x for k, v in flow_int.items() if v.x is not None and int(v.x) > 0},
        })

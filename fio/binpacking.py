from numbers import Number
from typing import Dict, List, Literal
import mip
from . import arith

# %%

# # Bin packing

# Inputs:
# * $v[j]$ output flow required
# * $u[i]$ input flow required

# Variables:
# * $x[i, j]$ real between 0 and 1, indicate the flow from $i$ to j$
# * $y[i, j]$ boolean indicate if the edge from $i$ to $j$

# Minimize $\displaystyle \sum_{i, j} y[i, j]$
# Subject:
# * $\displaystyle \forall i j, x[i, j] \leq y[i, j]$
# * $\displaystyle \forall i, \sum_j x[i, j] = u_i$
# * $\displaystyle \forall j, \sum_i x[i, j] = v_i$

# %%

def optimize(inputs: List[Number], outputs: List[Number]) -> Dict[int, Number]:
  m = mip.Model()
  m.verbose = 0

  assert arith.float_to_frac(sum(inputs)) == arith.float_to_frac(sum(outputs))

  x = {
    (i, j): m.add_var(f"flow_{i, j}", lb=0, ub=1)
    for i, _ in enumerate(inputs)
    for j, _ in enumerate(outputs)
  }
  y = {
    (i, j): m.add_var(
      f"flow_bool_{i, j}",
      lb=0,
      ub=1,
      var_type=mip.BINARY,
      obj=10000
    )
    for i, _ in enumerate(inputs)
    for j, _ in enumerate(outputs)
  }

  for i, _ in enumerate(inputs):
      for j, _ in enumerate(outputs):
          m.add_constr(x[i, j] <= y[i, j]*1)

  for i, v in enumerate(inputs):
      m.add_constr(mip.quicksum(x[i, j] for j, _ in enumerate(outputs)) == v)

  for j, v in enumerate(outputs):
      m.add_constr(mip.quicksum(x[i, j] for i, _ in enumerate(inputs)) == v)

  m.optimize(max_seconds=1)

  x = {k: arith.float_to_frac(v.x) for k, v in x.items() if arith.float_to_frac(v.x) > 0}
  y = {k: arith.float_to_frac(v.x) for k, v in y.items() if arith.float_to_frac(v.x) > 0}

  return x

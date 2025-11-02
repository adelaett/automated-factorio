from fractions import Fraction
from typing import Dict, List, Literal, Optional, Tuple
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



def optimize(inputs_: List[float], outputs_: List[float], weights:Optional[Dict[Tuple[float, float], float]]=None, timeout=10) -> Optional[Dict[tuple[int, int], Fraction]]:
  m = mip.Model()
  m.verbose = 0

  inputs = dict(enumerate(inputs_))

  outputs = dict(enumerate(outputs_))


  assert arith.float_to_frac(sum(inputs.values(), 0)) == arith.float_to_frac(sum(outputs.values()))

  x = {
    (i, j): m.add_var(f"flow_{i, j}", lb=0, ub=1) # type: ignore[arg-type]
    for i, _ in inputs.items()
    for j, _ in outputs.items()
  }
  y = {
    (i, j): m.add_var(
      f"flow_bool_{i, j}",
      lb=0, # type: ignore[arg-type]
      ub=1, # type: ignore[arg-type]
      var_type=mip.BINARY,
      obj=10000 if weights is None else weights[i, j] # type: ignore[arg-type]
    )
    for i, _ in inputs.items()
    for j, _ in outputs.items()
  }

  for i, _ in inputs.items():
      for j, _ in outputs.items():
          m.add_constr(x[i, j] <= y[i, j] * 1)

  for i, v in inputs.items():
      m.add_constr(mip.quicksum(x[i, j] for j, _ in outputs.items()) == v)

  for j, v in outputs.items():
      m.add_constr(mip.quicksum(x[i, j] for i, _ in inputs.items()) == v)

  m.optimize(max_seconds=timeout) # type: ignore[arg-type]

  if m.status in [mip.OptimizationStatus.FEASIBLE, mip.OptimizationStatus.OPTIMAL]:

    x = {k: arith.float_to_frac(v.x) for k, v in x.items() if arith.float_to_frac(v.x) > 0}
    # y = {k: arith.float_to_frac(v.x) for k, v in y.items() if arith.float_to_frac(v.x) > 0}

    return x
  
  else:
    print(m.status)
    return None

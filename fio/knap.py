import mip
import numpy as np

m = mip.Model()
m.verbose = 0
k = 10
x = m.add_var_tensor((10, ), "x", var_type="B")
y = m.add_var_tensor((10, ), "y", var_type="C")

for c in y <= x:
  m.add_constr(c)

w = np.random.rand(k)

m += w @ x

m.add_constr(mip.xsum(x) <= 7)
m.add_constr(mip.xsum(y) >= 4)

m.optimize()

print(m.status)
print([round(wi, 1) for wi in w])
print([xi.x for xi in x])
print([yi.x for yi in y])

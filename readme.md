# Factorio Auto-builder

This repository is a tentative in building a automatic factory builder for factorio.

Algorithm:

1. find the number of machines for each recipes.
2. use a bin-packing algorithm to match links between machines.
3. place the machines using a simple linear model. (objective = abs(x_i -x_j) + abs(y_i - y_j); subject to: x_i != x_j or y_i != y_j).
4. route between the differents machines. (for example using bots)
5. produce the corresponding blueprint. (widgets for each factory)

# For the placement & routing, we have two different options. the first one is to put it all inside a linear programming, and the second one is to use multiple steps. We go for the second one, as prototypes of the first approches makes it really very hard to find optimal solution without specialized algorithms.

# So, we need to find multiple steps to compute our approach. The first one is to code a wang tile set, and module it around desired frequencies, using a tile solver that pick a tile using random probabilities. We can go for a break-and-repair approach.

# 10 c
# 2 s 
# 5 p

# total throughput:
# 30 = c + s + p


# Factorio Auto-builder

An automatic factory layout generator for the video game Factorio. This tool analyzes production recipes and generates optimized factory blueprints.


> [!NOTE]  
> Following the factorio space age release, [quality](https://factorio.com/blog/post/fff-375) was added to the game. It was the occasion to update the code with new algorithms. The rewrite is in process. The two-stages mathematical modeling for quality-updated factorio is available [quality.ipynb](https://github.com/adelaett/automated-factorio/blob/main/notebooks/quality.ipynb). It requires Gurobi to run, and indicate what kind of modules should be used in order to get the least number of machines to perform a given product. It exports a graph in `gml` format. The graph can then be plotted using the [layout.ipynb](https://github.com/adelaett/automated-factorio/blob/main/notebooks/layout.ipynb) file. Blueprint generation for these is for the moment disabled.

## Features

- **Recipe Optimization**: Uses linear programming to determine optimal machine counts and production flows
- **Blueprint Processing**: Parse and generate Factorio blueprint strings with base64 encoding/decoding
- **Layout Generation**: Automatic placement of machines using mathematical optimization
- **Routing Algorithms**: Pathfinding for connecting machines (A* and Dijkstra implementations)
- **Bin Packing**: Efficient matching of input/output flows between machines
- **Multiple Mod Support**: Database files for base game, Angel's & Bob's mods, and Krastorio2

## Core Components

- `flow.py` - Linear programming optimization for production flows
- `blueprint.py` - Blueprint string parsing and generation utilities  
- `binpacking.py` - Bin packing algorithm for flow matching
- `placement.py` - Machine placement using Steiner tree algorithms
- `naive_routing.py` - A* pathfinding for connecting machines
- `database.py` - Game data loading and querying system
- `arith.py` - Mathematical utilities including fraction handling

## Algorithm Overview

1. Calculate optimal machine counts for recipes using linear programming
2. Match production flows between machines using bin packing
3. Place machines spatially using optimization models
4. Route connections between machines using pathfinding
5. Generate final blueprint string for import into Factorio

## Data Files

- `base.json` - Vanilla Factorio recipes and items
- `angels-bobs.json` - Angel's & Bob's modpack data  
- `krastorio2.json` - Krastorio2 mod data

## Related Work

### Academic Foundations
The algorithms implemented in this project are based on classical combinatorial optimization techniques from:
- **Combinatorial Optimization: Theory and Algorithm** (Springer) - https://link.springer.com/book/10.1007/978-3-662-56039-6

### Similar Factorio Tools
- **[Foreman2](https://github.com/DanielKote/Foreman2)** - Visual planning tool for Factorio production flowcharts
- **[Production Flow](https://github.com/Windfisch/production-flow)** - Graph-based production flow optimizer for Factorio
- **[Factorio Optimizer](https://github.com/meriton42/factorio-optimizer)** - Helps optimize Factorio factory layouts
- **[Factorio Tools](https://github.com/joelverhagen/FactorioTools)** - Tools for generating optimal oil field layouts
- **[Factorio Calculator](https://factoriocalculator.github.io/)** - Web-based calculator for production ratios and resource planning
- **[Kirk McDonald's Calculator](https://kirkmcdonald.github.io/)** - Popular web tool for Factorio production analysis

### Core Algorithms
- **Mixed Integer Linear Programming**: For optimizing production flows and machine counts
- **Bin Packing**: Classical optimization problem for matching input/output flows
- **Steiner Tree Problem**: Kou-Markowsky algorithm for optimal machine placement
- **Graph Pathfinding**: Dijkstra and A* algorithms for routing connections
- **Continued Fractions**: Exact continuous fractions for floating-point approximation & splitter computations.



### VS-code configuration

To use the notebooks configuration correctly, add `"jupyter.notebookFileRoot": "${workspaceFolder}"` to your configuration.


### MacOS

using `python-mip` on silicon apple requires to have the `0.16rc2` version at least, and a gcc compiler installed. if using macports and not homebrew you need to relink libgfortran

install_name_tool -change \
    /opt/homebrew/opt/gcc/lib/gcc/current/libgfortran.5.dylib \
    /opt/local/lib/libgcc/libgfortran.5.dylib \
    .venv/lib/python3.11/site-packages/mip/libraries/cbc-c-darwin-arm64.dylib

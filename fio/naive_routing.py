import heapq

from collections import defaultdict
from fio.mytypes import Position


"""This files implement a naive routing algorithm.

It is only the A^* algorithm, implemented using a grid with 3*3 cells. A mask is provided to build-up multiple paths when needed.

Each of the cells are of one type LU (starts on the left, finishes on up), LR, LD, etc...


This algorithm may return None if no path is possible. This is possible in the advent of either an absence of path, or when the path found is invalid because looping. However, Dijstra algorithm should always return the optimal path, hence should be valid.
"""

def identify_successors(mask: dict[Position, bool], source: Position) -> list[tuple[int, Position]]:
  l: list[tuple[int, Position]] = []
  for i in range(1, 2+1):
    l.append((i, Position(source.x+i, source.y)))
    l.append((i, Position(source.x-i, source.y)))
    l.append((i, Position(source.x, source.y+1)))
    l.append((i, Position(source.x, source.y-1)))
  
  return [(d, p) for (d, p) in l if not mask[p]]

def dijstra(mask: dict[Position, bool], source: Position, target: Position):
  prev: dict[Position, Position] = dict()
  best: dict[Position, float] = defaultdict(lambda: float("inf"))

  queue = [(0, source)]

  while queue:
    d, current = heapq.heappop(queue)

    for delta, n in identify_successors(mask, current):
      if d + delta < best[n]:
        best[n] = d + delta**2
        prev[n] = current
        heapq.heappush(queue, (d + delta**2, n))

      if n == target:
        break
    else:
      continue
    break
  
  if target in prev:
    path = [target]
    while path[-1] != source:
      path.append(prev[path[-1]])

    return list(reversed(path))
  else:
    return None


def test_simple():
  assert dijstra(defaultdict(bool), Position(3, 3), Position(5, 5)) == [Position(x=3, y=3), Position(x=3, y=4), Position(x=3, y=5), Position(x=5, y=5)]

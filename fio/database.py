import jq
import json
from pathlib import Path

class bunch(dict):
  def __getattribute__(self, name: str):
    try:
      return super().__getattribute__(name)
    except AttributeError:
      return self[name]

class table(bunch):
  def find(self, cmd):
    return jq.compile(cmd).input(self).all()

  def query(self, cmd):
    return jq.compile(cmd).input(self).first()


def load_db(path: Path | str) -> bunch:
  """Load a json database containing multiple tables."""

  return bunch({k: table(v) for k, v in json.load(open(path)).items()})


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


def get_recipes(params):
  pass


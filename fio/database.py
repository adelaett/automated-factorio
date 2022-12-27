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
  """Load a json database from a folder."""
  db = bunch()
  for f in Path(path).glob("*.json"):
    db[f.stem.replace("-", "_")] = table(json.load(open(f)))
  return db

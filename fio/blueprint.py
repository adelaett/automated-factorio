import base64
import zlib
import json
import copy

from .mytypes import *


def parse_blueprint_string(blueprint_base64):
    assert isinstance(blueprint_base64, str)
    version = int(blueprint_base64[0])
    assert version == 0, 'Blueprint version number ' + str(version) + ' is not among the supported versions: ' + str(0)
    return json.dumps(json.loads(zlib.decompress(base64.b64decode(blueprint_base64[1:])).decode()), indent=2)

def generate_blueprint_string(blueprint_json):
    assert isinstance(blueprint_json, str)
    return str(0) + base64.b64encode(zlib.compress(blueprint_json.encode())).decode()

def generate(blueprint):
    return generate_blueprint_string(json.dumps(blueprint))

def loads(x):
    return json.loads(zlib.decompress(base64.b64decode(x[1:])).decode())

def dumps(bp):
    return generate_blueprint_string(json.dumps(bp))


def bp_from_entities(entities):
    return {"blueprint": {"icons": [],"entities": entities,"item": "blueprint","version": 281479275675648}}


### Functions that manipulate blueprints to translate it, or to generate bounding boxes.


def boundingbox(entities):
    # Get the bounding box of the blueprint
    x = []
    y = []
    for e in entities:
        x.append(e["position"]["x"])
        y.append(e["position"]["y"])
    
    return (min(x), min(y), max(x), max(y))

def size(entities):
    # Generate the size of an blueprint
    x1, y1, x2, y2 = boundingbox(entities)
    return x2 - x1 + 1, y2 - y1 + 1

def translate(dx, dy, entities):
    # translate a blueprint
    for e in entities:
        e["position"]["x"] += dx
        e["position"]["y"] += dy


from itertools import count
def recount(entities):
    new = []
    c = count(1)
    for e in entities:
        e = copy.deepcopy(e)
        e["entity_number"] = next(c)
    
        new.append(e)
        
    return new


def merge(blueprints):
    """Merge multiple blueprints with unique entity numbers and offset wires."""
    if not blueprints:
        return None
    
    merged = {
        'blueprint': {
            'icons': blueprints[0]['blueprint'].get('icons', []),
            'entities': [],
            'wires': [],
            'item': 'blueprint',
            'version': blueprints[0]['blueprint'].get('version', 562949958139904)
        }
    }
    
    offset = 0
    
    for bp in blueprints:
        entities = bp['blueprint'].get('entities', [])
        wires = bp['blueprint'].get('wires', [])
        
        # Offset entities
        for entity in entities:
            new_entity = entity.copy()
            new_entity['entity_number'] += offset
            merged['blueprint']['entities'].append(new_entity)
        
        # Offset wires [source_entity, source_connector, target_entity, target_connector]
        for wire in wires:
            merged['blueprint']['wires'].append([
                wire[0] + offset,  # source entity
                wire[1],           # source connector
                wire[2] + offset,  # target entity
                wire[3]            # target connector
            ])
        
        # Update offset to max entity number
        if entities:
            offset = max(e['entity_number'] for e in merged['blueprint']['entities'])
    
    return merged

def clean(entities):
    # Cleanup the blueprint
    x1, y1, x2, y2 = boundingbox(entities)
    
    translate(-x1, -y1, entities)

def clean_recursive(d):
    if type(d) == dict:
        return {k: clean_recursive(v) if k != "entities" else clean(v) for k, v in d.items()}
    elif type(d) == list:
        return [clean_recursive(v) for v in d]
    else:
        return d


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Load and read blueprints for factorio (https://www.factorio.com/)")
    parser.add_argument('-l', "--load", action='store_true')
    parser.add_argument('-d', "--dump", action='store_true')
    parser.add_argument('-c', "--clean", action='store_true')
    args = parser.parse_args()

    assert not (args.load and args.dump)

    if args.load and not args.clean:
        print(json.dumps(loads(sys.stdin.read()), indent=2))

    if args.load and args.clean:
        print(json.dumps(clean_recursive(loads(sys.stdin.read())), indent=2))

    if args.dump:
        print(generate_blueprint_string(sys.stdin.read()))

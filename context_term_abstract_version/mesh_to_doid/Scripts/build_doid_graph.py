from __future__ import unicode_literals, print_function
import codecs
import pickle
from pprint import pprint
import sys

def iter_doid_obo(obo_path):
    with codecs.open(obo_path, 'r', 'utf8') as f:
        block = None
        for line in f:
            line = line.strip()

            if len(line) == 0:
                continue

            if line == '[Term]':
                if block is not None and len(block) > 0:
                    yield block
                block = []
                continue

            if block is not None:
                block.append(line)

        if len(block) > 0:
            yield block


def create_doid_obj(block):
    obj = {
        'synonym': set(), 
        'parent': set(), 
        'grandparent': set(),
        'child': set(),
        'grandchild': set(),
        'sibling': set(),
        'xref': set()
    }
    for line in block:
        if line.startswith('id: '):
            doid = line[4:].strip()
            obj['doid'] = doid
        elif line.startswith('is_a: '):
            parent = line[6:].split('!')[0].strip()
            obj['parent'].add(parent)
        elif line.startswith('name: '):
            name = line[6:].strip().lower()
            obj['name'] = name
        elif line.startswith('synonym: '):
            if 'EXACT' not in line:
                continue
            synonym = line.split('"')[1].lower()
            obj['synonym'].add(synonym)
        elif line.startswith('xref: '):
            xref = line[6:].strip()
            obj['xref'].add(xref)
    return obj


def propagate(graph):
    for doid, obj in graph.items():
        for parent in obj['parent']:
            parent_obj = graph[parent]
            parent_obj['child'].add(doid)            

            for grandparent in parent_obj['parent']:
                grandparent_obj = graph[grandparent]
                grandparent_obj['grandchild'].add(doid)                
                obj['grandparent'].add(grandparent)

    for doid, obj in graph.items():
        for parent in obj['parent']:
            parent_obj = graph[parent]
            for child in parent_obj['child']:
                if child != doid:
                    obj['sibling'].add(child)


if __name__ == '__main__':
    graph = {}
    name_to_doid = {}
    doid_obo_file = sys.argv[1]
    for block in iter_doid_obo(doid_obo_file):
        obj = create_doid_obj(block)
        graph[obj['doid']] = obj
        
        name_to_doid[obj['name']] = obj['doid']
        for syn in obj['synonym']:
            name_to_doid[syn] = obj['doid']

    propagate(graph)
    pprint(graph['DOID:1324'])
    with open('../Files/doid_graph.pk', 'wb') as f:
        pickle.dump(graph, f)

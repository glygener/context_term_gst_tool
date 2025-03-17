import sys
import pickle
from pprint import pprint
import sys

doid_graph_path = "/usa/shovan/Glygen/mesh_to_doid/Files/doid_graph.pk"
with open(doid_graph_path, 'rb') as f:
    doid_graph = pickle.load(f)

def get_doid_dicts():
    doid_to_name = dict()
    mesh_to_doid = dict()
    name_to_doid = dict()

    for doid in doid_graph.keys():
        obj = doid_graph[doid]
        
        doid_name = obj['name']
        doid_to_name[doid] = doid_name
        xrefs = obj['xref']
        for xref in xrefs:
            if xref.startswith("MESH:"):
                mesh_id = xref
                if mesh_id in mesh_to_doid: mesh_to_doid[mesh_id].add(doid)
                else: mesh_to_doid[mesh_id] = set([obj['doid']])
        
        name_to_doid[obj['name'].lower()] = set([obj['doid']])
        for syn in obj['synonym']:
            name_to_doid[syn.lower()] = set([obj['doid']])
    return (doid_to_name, mesh_to_doid, name_to_doid)


    
def run():
    (doid_to_name, mesh_to_doid, name_to_doid) = get_doid_dicts()
    pprint(doid_to_name["DOID:162"])
    pprint(mesh_to_doid["MESH:D009369"])
    pprint(name_to_doid["lung cancer"])
    
    doid_to_name_file = "/usa/shovan/Glygen/mesh_to_doid/Files/doid_to_name.pk"
    mesh_to_doid_file = "/usa/shovan/Glygen/mesh_to_doid/Files/mesh_to_doid.pk"
    name_to_doid_file = "/usa/shovan/Glygen/mesh_to_doid/Files/name_to_doid.pk"
    with open(doid_to_name_file, 'wb') as handle:
        pickle.dump(doid_to_name, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(mesh_to_doid_file, 'wb') as handle:
        pickle.dump(mesh_to_doid, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(name_to_doid_file, 'wb') as handle:
        pickle.dump(name_to_doid, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    run()

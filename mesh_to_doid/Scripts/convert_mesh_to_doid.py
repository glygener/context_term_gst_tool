import sys
import pickle
from pymongo import MongoClient
from pprint import pprint
import sys
reload(sys);
sys.setdefaultencoding("utf8")
client = MongoClient('localhost')
db = client.pubtator2018.medline.aligned


doid_graph_path = "../Files/doid_graph.pk"
with open(doid_graph_path, 'rb') as f:
    doid_graph = pickle.load(f)

cancer_doid_path = "../Files/cancer_doids.pk"
with open(cancer_doid_path, 'rb') as f:
    cancer_doids_dict = pickle.load(f)

cancer_doids = cancer_doids_dict['cancer_doids']


doid_to_name_file = "../Files/doid_to_name.pk"
mesh_to_doid_file = "../Files/mesh_to_doid.pk"
name_to_doid_file = "../Files/name_to_doid.pk"
with open(doid_to_name_file, 'rb') as handle:
    doid_to_name = pickle.load(handle)
with open(mesh_to_doid_file, 'rb') as handle:
    mesh_to_doid = pickle.load(handle)
with open(name_to_doid_file, 'rb') as handle:
    name_to_doid = pickle.load(handle)

###takes a set of doids and returns true if any one is a child of cancer
def is_doid_cancer(doids):
    if not doids: return False
    for doid in doids:
        if doid in cancer_doids: return True
    return False
        
def map_mesh_to_doid(mesh_to_doid, name_to_doid, mesh_id, mention=None):
    if mention and mention.lower() in name_to_doid: 
        return name_to_doid[mention.lower()]
    if mesh_id in mesh_to_doid: 
        return mesh_to_doid[mesh_id]
    elif mention and mention.lower() in name_to_doid: 
        return name_to_doid[mention.lower()]
    else: return None


def run():
    
    print("\nTesting MESH to DOID and cancer flag....")
    test_mesh_ids = ["MESH:D002289", "MESH:D034062"]
    for test_mesh_id in test_mesh_ids:
        doids = map_mesh_to_doid(mesh_to_doid, name_to_doid, test_mesh_id)
        is_cancer = is_doid_cancer(doids)
        print((test_mesh_id, doids, is_cancer))

    ####test with name/mention lookup; 
    ####this is important when the mesh id is wrong from pubtator, but the mention is correct
    print("\nTesting name lookup....")
    doid_breast_cancer = map_mesh_to_doid(mesh_to_doid, name_to_doid, "MESH:D001943") ##mesh right
    print(("Correct Mesh:",doid_breast_cancer))
    doid_breast_cancer = map_mesh_to_doid(mesh_to_doid, name_to_doid, "MESH:D009369") ##mesh wrong 
    print(("MESH Wrong:",doid_breast_cancer))

    ##mesh wrong but mention from pubtator correct
    ### in this case if mention is specified use it first to get DOID
    doid_breast_cancer = map_mesh_to_doid(mesh_to_doid, name_to_doid, "MESH:D009369", mention="breast cancer")
    print(("MESH Wrong + name lookup:",doid_breast_cancer))

if __name__ == '__main__':
    run()

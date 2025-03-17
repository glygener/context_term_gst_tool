import sys
import pickle

graph_path = "../Files/doid_graph.pk" 
with open(graph_path, 'rb') as f:
    doid_graph = pickle.load(f)

cancer_doids = { 'cancer_doids': set()}

def get_child_nodes(doid, res):
    obj = doid_graph[doid]
    if 'child' not in obj: return res
    for child_doid in obj['child']:
        res.add(child_doid)
        get_child_nodes(child_doid, res)

def get_cancer_child_doids(doid):
    doids = list()
    obj = doid_graph[doid]

    for child_doid in obj['child']:
        print(child_doid)
        cancer_doids['cancer_doids'].add(child_doid)
        get_cancer_child_doids(child_doid)

def run():
    cancer_doids['cancer_doids'].add("DOID:162")
    print("DOID:162")
    get_cancer_child_doids("DOID:162")
    with open('../Files/cancer_doids.pk', 'wb') as f:
        pickle.dump(cancer_doids, f)
    
if __name__ == '__main__':
    run()

from pymongo import MongoClient
from pprint import pprint
import pickle

from importlib import reload ###if using python3
import sys
reload(sys);
#sys.setdefaultencoding("utf8") #uncomment if using python2
client = MongoClient('localhost')
#db = client.pubtator.medline.aligned
db = client.pubtator2018.medline.aligned

#doid_to_name_file = "../Files/doid_to_name.pk"
mesh_to_doid_file = "../Files/mesh_to_doid.pk"
name_to_doid_file = "../Files/name_to_doid.pk"
#with open(doid_to_name_file, 'rb') as handle:
#    doid_to_name = pickle.load(handle)
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


def getDiseases(pmid):
    print_dict = dict()
    doc = db.find_one({'docId': pmid})
    gene_entities = list()
    if doc and doc['entity']:
        entities = doc['entity']
        for key,entity in entities.items():
            if entity['entityType'] == 'Disease' and entity['source'] == 'PUBTATOR':
                #print(entity)
                entity_ids = entity['entityId']
                entity_text = entity['entityText']
                sent_num = -1
                if 'sentenceIndex' in entity.keys():
                    sent_num = entity['sentenceIndex']
                for entity_id in entity_ids:
                    entity_id_string = entity_id['idString']
                    entity_id_source = entity_id['source']
                    if sent_num != -1 and entity_text != "":
                        mesh_id = entity_id_source+":"+entity_id_string 
                        doid = map_mesh_to_doid(mesh_to_doid, name_to_doid, mesh_id, mention=entity_text)
                        if not doid:
                            doid = set([mesh_id])
                        doid_str = ";".join(doid)
                        to_print = (str(pmid),str(sent_num),doid_str,entity_text)
                        if to_print not in print_dict:
                            print("\t".join(to_print))
                        else:
                            print_dict[to_print] = True

def run(doc_ids_file):
    doc_ids_FH = open(doc_ids_file, "r")
    doc_ids = doc_ids_FH.readlines()
    doc_ids_FH.close()
    for doc_id in doc_ids:
        doc_id = doc_id.rstrip()
        getDiseases(doc_id)

if __name__ == '__main__':
   run(sys.argv[1])


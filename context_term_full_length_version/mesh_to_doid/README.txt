Path: /data/Applications/sgupta/mesh_to_doid

There are several scripts in the Scripts folder each with a different function:

1. Building the DOID graph from obo file

Script name: build_doid_graph.py 

Usage: python build_doid_graph.py ./Input/doid.obo

Output parse the tree structure of the doid.obo file and dumps it into a pickle file (./Files/doid_graph.pk)

Note, the doid.obo is updated by DO (not sure about how frequently). The obo file can downloaded from https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/doid.obo



2.  Read the doid graph and dump necessary mapping dictionaries

Script name: dump_doid_dicts.py

Outputs three pickled dictionaries:

(a) ./Files/doid_to_name.pk: mapping from a doid to its normalized name
(b) ./Files/mesh_to_doid.pk: mapping from a mesh id to doids
(c) ./Files/name_to_doid.pk:  mapping from a name to doid (this will be useful when the mesh id from a tool such as PubTator is wrong)


3. Get cancer DOIDs

Script name: get_cancer_doids.py

Outputs a pickled set of cancer doids

Basically this script traverses the DO tree from DOID:162 (cancer) and recursively gets all its child DOID


4. Sample test script to map mesh id to DOID

Script name: convert_mesh_to_doid.py
The main function is map_mesh_to_doid(mesh_to_doid, name_to_doid, mesh_id, mention=None)

The script is self-explanatory and in the run method I have some sample usage. The only thing to note is the last argument “mention”
Sometime a tool like Pubtator will output an incorrect MESH ID but a correct mention. (eg. MESH for cancer but mention was “breast cancer”)
If the mention argument is provided in the above function, it will first do the DOID mapping using the name and then if that fails it will use the MESH ID.

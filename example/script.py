from openalea.core.alea import load_package_manager, function, get_node
pm = load_package_manager()

#way 1 if the composite node has inputs and outputs 

node_factory = pm['alinea.phenomenal.macros']['phenoarch demo pipeline']
pipeline = function(node_factory)

output = pipeline('./bibi.png')


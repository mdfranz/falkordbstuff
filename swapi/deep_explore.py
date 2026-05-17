import os
from falkordb import FalkorDB

db = FalkorDB(host=os.getenv('FALKORDB_HOST', 'localhost'), port=int(os.getenv('FALKORDB_PORT', 6379)))

print(f"Graphs: {db.list_graphs()}")

g = db.select_graph('social_copy')

# Property keys
try:
    keys = g.ro_query("CALL db.propertyKeys()").result_set
    print(f"Property Keys: {[k[0] for k in keys]}")
except Exception as e:
    print(f"Error getting property keys: {e}")

# Check for nodes with ANY label
try:
    labeled_nodes_count = g.ro_query("MATCH (n) WHERE labels(n) <> [] RETURN count(n)").result_set[0][0]
    print(f"Labeled nodes count: {labeled_nodes_count}")
except Exception as e:
    print(f"Error checking for labeled nodes: {e}")

# Check for distinct property values for 'v'
try:
    distinct_v = g.ro_query("MATCH (n) RETURN DISTINCT n.v").result_set
    print(f"Distinct values for 'v': {[v[0] for v in distinct_v]}")
except Exception as e:
    print(f"Error getting distinct 'v' values: {e}")

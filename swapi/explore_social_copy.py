from falkordb import FalkorDB

db = FalkorDB(host='localhost', port=6379)
g = db.select_graph('social_copy')

print(f"--- Exploring graph: social_copy ---")

# 1. Labels
try:
    labels = g.ro_query("CALL db.labels()").result_set
    print(f"Labels: {[l[0] for l in labels]}")
except Exception as e:
    print(f"Error getting labels: {e}")

# 2. Relationship Types
try:
    rel_types = g.ro_query("CALL db.relationshipTypes()").result_set
    print(f"Relationship Types: {[r[0] for r in rel_types]}")
except Exception as e:
    print(f"Error getting relationship types: {e}")

# 3. Counts
try:
    node_count = g.ro_query("MATCH (n) RETURN count(n)").result_set[0][0]
    rel_count = g.ro_query("MATCH ()-[r]->() RETURN count(r)").result_set[0][0]
    print(f"Node count: {node_count}")
    print(f"Relationship count: {rel_count}")
except Exception as e:
    print(f"Error getting counts: {e}")

# 4. Sample Nodes
try:
    print("\nSample Nodes:")
    nodes = g.ro_query("MATCH (n) RETURN n LIMIT 5").result_set
    for row in nodes:
        print(row[0])
except Exception as e:
    print(f"Error sampling nodes: {row[0]}")

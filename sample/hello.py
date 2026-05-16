from falkordb import FalkorDB

# Connect to FalkorDB
db = FalkorDB(host='localhost', port=6379)

# Select the social graph
g = db.select_graph('social')

# Create 100 nodes and return a handful
nodes = g.query('UNWIND range(0, 100) AS i CREATE (n {v:1}) RETURN n LIMIT 10').result_set
for n in nodes:
    print(n)

# Read-only query the graph for the first 10 nodes
nodes = g.ro_query('MATCH (n) RETURN n LIMIT 10').result_set

# Copy the Graph
copy_graph = g.copy('social_copy')

# Delete the Graph
g.delete()

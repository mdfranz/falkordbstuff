import os
from falkordb import FalkorDB

try:
    db = FalkorDB(host=os.getenv('FALKORDB_HOST', 'localhost'), port=int(os.getenv('FALKORDB_PORT', 6379)))
    graphs = db.list_graphs()
    print(f"Available graphs: {graphs}")
except Exception as e:
    print(f"Error connecting to FalkorDB or listing graphs: {e}")

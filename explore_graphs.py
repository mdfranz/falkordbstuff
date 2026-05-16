from falkordb import FalkorDB

try:
    db = FalkorDB(host='localhost', port=6379)
    graphs = db.list_graphs()
    print(f"Available graphs: {graphs}")
except Exception as e:
    print(f"Error connecting to FalkorDB or listing graphs: {e}")

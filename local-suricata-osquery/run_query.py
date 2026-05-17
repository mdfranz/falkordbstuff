import argparse
import sys
from falkordb import FalkorDB
from prettytable import PrettyTable

def run_query(query_file, graph_name='suricata'):
    try:
        with open(query_file, 'r') as f:
            query = f.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{query_file}' not found.")
        return

    if not query:
        print("Error: Query file is empty.")
        return

    print(f"Executing query from {query_file}:\n{'-'*40}\n{query}\n{'-'*40}")

    try:
        db = FalkorDB(host='localhost', port=6379)
        graph = db.select_graph(graph_name)
        
        result = graph.query(query)
        
        if not result.result_set:
            print("No results found.")
            return

        # Prepare and print table
        headers = result.header
        table = PrettyTable(headers)
        
        for row in result.result_set:
            # Handle lists/dicts in the output by converting to strings
            clean_row = [str(col) if isinstance(col, (list, dict)) else col for col in row]
            table.add_row(clean_row)
            
        print(table)
        print(f"\nTotal rows: {len(result.result_set)}")

    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Cypher query against FalkorDB from a text file.")
    parser.add_argument("query_file", help="Path to the file containing the Cypher query.")
    parser.add_argument("--graph", default="suricata", help="Name of the FalkorDB graph to query (default: 'suricata').")
    
    args = parser.parse_args()
    run_query(args.query_file, args.graph)

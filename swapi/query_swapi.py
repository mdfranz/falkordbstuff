from falkordb import FalkorDB
import json

def run_query(g, query, title):
    print(f"\n--- {title} ---")
    print(f"Query: {query}")
    try:
        result = g.ro_query(query)
        # Handle cases where result_set might be empty or have different structures
        if result.result_set:
            # Print headers if available
            print("Results:")
            for row in result.result_set:
                print(row)
        else:
            print("No results found.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('starwars')

    # 1. Basic counts
    run_query(g, "MATCH (n) RETURN labels(n)[0] as label, count(n)", "Node Counts by Label")

    # 2. Relationship counts
    run_query(g, "MATCH ()-[r]->() RETURN type(r) as type, count(r)", "Relationship Counts by Type")

    # 3. Multi-hop: Characters in 'A New Hope' and their homeworlds
    run_query(g, """
        MATCH (f:Film {title: 'A New Hope'})<-[:APPEARED_IN]-(p:Person)-[:BORN_ON]->(pl:Planet)
        RETURN p.name, pl.name
    """, "Characters in 'A New Hope' and their Homeworlds")

    # 4. Aggregation: Top planets by character count
    run_query(g, """
        MATCH (pl:Planet)<-[:BORN_ON]-(p:Person)
        RETURN pl.name, count(p) as char_count
        ORDER BY char_count DESC
        LIMIT 5
    """, "Top Planets by Character Count")

    # 5. Shared Films: Who appeared in the most films together? (Sample)
    run_query(g, """
        MATCH (p1:Person)-[:APPEARED_IN]->(f:Film)<-[:APPEARED_IN]-(p2:Person)
        WHERE p1.name < p2.name
        RETURN p1.name, p2.name, count(f) as shared_films
        ORDER BY shared_films DESC
        LIMIT 5
    """, "Characters with Most Shared Films")

if __name__ == "__main__":
    main()

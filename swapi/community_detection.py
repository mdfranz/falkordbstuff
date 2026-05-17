import os
from falkordb import FalkorDB

def main():
    db = FalkorDB(host=os.getenv('FALKORDB_HOST', 'localhost'), port=int(os.getenv('FALKORDB_PORT', 6379)))
    g = db.select_graph('starwars')

    print("--- Star Wars Community Detection (Shared Film Clusters) ---")
    
    # We'll use a simple "Shared Film" metric to identify clusters.
    # A 'community' here is defined by characters who appear in the same sets of films.
    
    query = """
        MATCH (p1:Person)-[:APPEARED_IN]->(f:Film)<-[:APPEARED_IN]-(p2:Person)
        WHERE p1.name < p2.name
        WITH p1, p2, count(f) as shared_count
        WHERE shared_count >= 3
        RETURN p1.name, p2.name, shared_count
        ORDER BY shared_count DESC
    """
    
    print("\nStrongly Connected Pairs (Shared 3+ Films):")
    results = g.ro_query(query).result_set
    for row in results:
        print(f"{row[0]} <--> {row[1]} ({row[2]} films)")

    # Identify the "Hub" characters (highest degree of shared appearances)
    hub_query = """
        MATCH (p:Person)-[:APPEARED_IN]->(f:Film)
        WITH p, count(f) as film_count
        RETURN p.name, film_count
        ORDER BY film_count DESC
        LIMIT 5
    """
    print("\nTop Hub Characters (Appear in most films):")
    hubs = g.ro_query(hub_query).result_set
    for row in hubs:
        print(f"{row[0]}: {row[1]} films")

    # Grouping by "Trilogy Focus" (Experimental)
    # Since SWAPI IDs usually map to release order, we can approximate:
    # Ep 4,5,6 (Original) vs Ep 1,2,3 (Prequel)
    
    trilogy_query = """
        MATCH (p:Person)-[:APPEARED_IN]->(f:Film)
        WITH p, 
             collect(f.episode_id) as episodes
        WITH p, episodes,
             ALL(e IN episodes WHERE e IN [1,2,3]) as PrequelOnly,
             ALL(e IN episodes WHERE e IN [4,5,6]) as OriginalOnly,
             ANY(e IN episodes WHERE e IN [1,2,3]) AND ANY(e IN episodes WHERE e IN [4,5,6]) as CrossEra
        RETURN 
            CASE 
                WHEN CrossEra THEN 'Cross-Era (Hubs)'
                WHEN PrequelOnly THEN 'Prequel Trilogy'
                WHEN OriginalOnly THEN 'Original Trilogy'
                ELSE 'Other'
            END as Community,
            collect(p.name) as Members
    """
    print("\nCommunity Clustering by Trilogy Appearance:")
    clusters = g.ro_query(trilogy_query).result_set
    for row in clusters:
        print(f"\n[{row[0]}]")
        print(", ".join(row[1]))

if __name__ == "__main__":
    main()

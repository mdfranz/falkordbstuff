import json
import os
import urllib.request
from falkordb import FalkorDB

import ssl

# Create an unverified context for urllib to bypass expired certificates
ssl_context = ssl._create_unverified_context()

def fetch_data(url):
    print(f"Fetching: {url}")
    with urllib.request.urlopen(url, context=ssl_context) as response:
        return json.loads(response.read().decode())

def fetch_all(endpoint):
    results = []
    url = f"https://swapi.dev/api/{endpoint}/"
    while url:
        data = fetch_data(url)
        results.extend(data['results'])
        url = data['next']
        # Limit to 2 pages for demo purposes to avoid long waits
        if len(results) >= 20:
            break
    return results

def main():
    db = FalkorDB(host=os.getenv('FALKORDB_HOST', 'localhost'), port=int(os.getenv('FALKORDB_PORT', 6379)))
    # Delete existing starwars graph if it exists for a clean start
    try:
        db.select_graph('starwars').delete()
    except:
        pass
    
    g = db.select_graph('starwars')

    print("Fetching People...")
    people = fetch_all('people')
    print("Fetching Films...")
    films = fetch_all('films')
    print("Fetching Planets...")
    planets = fetch_all('planets')

    # 1. Create Planets
    print("Importing Planets...")
    for p in planets:
        g.query("CREATE (:Planet {name: $name, terrain: $terrain, population: $population, url: $url})", 
                {'name': p['name'], 'terrain': p['terrain'], 'population': p['population'], 'url': p['url']})
    
    # 2. Create Films
    print("Importing Films...")
    for f in films:
        g.query("CREATE (:Film {title: $title, episode_id: $episode_id, release_date: $release_date, url: $url})", 
                {'title': f['title'], 'episode_id': f['episode_id'], 'release_date': f['release_date'], 'url': f['url']})

    # 3. Create People and Relationships
    print("Importing People and Relationships...")
    for p in people:
        # Create Person
        g.query("CREATE (:Person {name: $name, gender: $gender, url: $url})", 
                {'name': p['name'], 'gender': p['gender'], 'url': p['url']})
        
        # Link to Planet (Homeworld)
        g.query("""
            MATCH (p:Person {url: $person_url}), (pl:Planet {url: $planet_url})
            CREATE (p)-[:BORN_ON]->(pl)
        """, {'person_url': p['url'], 'planet_url': p['homeworld']})

        # Link to Films
        for film_url in p['films']:
            g.query("""
                MATCH (p:Person {url: $person_url}), (f:Film {url: $film_url})
                CREATE (p)-[:APPEARED_IN]->(f)
            """, {'person_url': p['url'], 'film_url': film_url})

    # Add some indices for better performance
    g.query("CREATE INDEX FOR (p:Person) ON (p.name)")
    g.query("CREATE INDEX FOR (f:Film) ON (f.title)")
    g.query("CREATE INDEX FOR (pl:Planet) ON (pl.name)")

    print("Import Complete!")

if __name__ == "__main__":
    main()

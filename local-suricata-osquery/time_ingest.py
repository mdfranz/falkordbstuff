import time
from pathlib import Path
from falkordb import FalkorDB
from parsers import parse_suricata

DATA_DIR = Path("data")
SAMPLE_FILE = DATA_DIR / "sample.json"

def time_test():
    try:
        db = FalkorDB(host='localhost', port=6379)
        # We use a separate temporary graph for the timing test
        graph = db.select_graph('timing_test')
        try:
            graph.delete()
        except:
            pass
        graph = db.select_graph('timing_test')
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"Starting timing test on 5000 events...")
    start_time = time.time()
    count = 0
    
    for event in parse_suricata(SAMPLE_FILE):
        if event['type'] == 'flow':
            query = "MERGE (src:IPAddress {ip: $src_ip}) MERGE (dst:IPAddress {ip: $dst_ip}) CREATE (src)-[:NETWORK_FLOW {ts: $ts}]->(dst)"
            params = {'src_ip': event['src'], 'dst_ip': event['dest'], 'ts': event['timestamp']}
            graph.query(query, params)
        elif event['type'] == 'tls_handshake':
            if event['hostname']:
                query = "MERGE (hn:Hostname {name: $hn}) MERGE (dst:IPAddress {ip: $dst_ip}) CREATE (hn)-[:OBSERVED_ON {source: 'tls'}]->(dst)"
                params = {'hn': event['hostname'], 'dst_ip': event['dest']}
                graph.query(query, params)
        
        count += 1

    end_time = time.time()
    duration = end_time - start_time
    eps = count / duration if duration > 0 else 0
    
    print(f"Processed {count} events in {duration:.2f} seconds.")
    print(f"Throughput: {eps:.2f} events/sec")
    
    graph.delete()

if __name__ == "__main__":
    time_test()

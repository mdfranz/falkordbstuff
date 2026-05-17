import argparse
import os
import time
from pathlib import Path
from falkordb import FalkorDB
from parsers import parse_suricata, parse_osquery

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def main(include_osquery=False, flow_only=False, batch_size=1000, limit=None, reset=False, start_from=None):
    try:
        db = FalkorDB(host=os.getenv('FALKORDB_HOST', 'localhost'), port=int(os.getenv('FALKORDB_PORT', 6379)))
        if reset:
            print("Resetting graph 'suricata'...")
            try:
                db.select_graph('suricata').delete()
            except:
                pass
        graph = db.select_graph('suricata')
    except Exception as e:
        print(f"Error connecting to FalkorDB: {e}")
        return

    # Indexes — critical for MERGE performance and Web UI query latency
    for stmt in (
        "CREATE INDEX FOR (n:IPAddress) ON (n.ip)",
        "CREATE INDEX FOR (n:Hostname) ON (n.name)",
        "CREATE INDEX FOR (n:Fingerprint) ON (n.id)",
    ):
        try:
            graph.query(stmt)
        except Exception:
            pass

    mode_str = "FLOWS ONLY" if flow_only else "FULL"
    print(f"Ingesting Suricata events ({mode_str}, batched)...")
    suricata_files = sorted(DATA_DIR.glob('eve*.json'))
    if not suricata_files:
        print(f"No Suricata files found in {DATA_DIR}")
        return
    
    if start_from:
        suricata_files = [f for f in suricata_files if f.name >= start_from]
        if not suricata_files:
            print(f"No files found at or after '{start_from}'")
            return
        print(f"Resuming from {suricata_files[0].name} ({len(suricata_files)} files remaining)")

    if limit:
        suricata_files = suricata_files[:limit]
    
    total_count = 0
    
    # Buffers for different event types
    buffers = {
        'flow': [],
        'dns_query': [],
        'dns_answer': [],
        'http_request': [],
        'tls_handshake': [],
        'ja4': [],
        'quic_event': []
    }

    def run_query(graph_obj, query, params, retries=3, delay=5):
        for attempt in range(retries):
            try:
                graph_obj.query(query, params)
                return
            except Exception as e:
                print(f"  Query error (attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    print("  Skipping batch after repeated failures.")

    def flush_buffers(graph_obj, force=False):
        # 1. Flows — aggregate per (src, dst, proto)
        if len(buffers['flow']) >= batch_size or (force and buffers['flow']):
            query = """
            UNWIND $events AS e
            MERGE (src:IPAddress {ip: e.src})
            ON CREATE SET src.name = e.src
            MERGE (dst:IPAddress {ip: e.dest})
            ON CREATE SET dst.name = e.dest
            MERGE (src)-[r:NETWORK_FLOW {proto: e.proto, port: e.dest_port}]->(dst)
            ON CREATE SET r.count = 1,
                          r.bytes_toserver = COALESCE(e.bytes_toserver, 0),
                          r.bytes_toclient = COALESCE(e.bytes_toclient, 0),
                          r.first_seen = e.timestamp,
                          r.last_seen = e.timestamp
            ON MATCH SET  r.count = r.count + 1,
                          r.bytes_toserver = r.bytes_toserver + COALESCE(e.bytes_toserver, 0),
                          r.bytes_toclient = r.bytes_toclient + COALESCE(e.bytes_toclient, 0),
                          r.last_seen = e.timestamp
            """
            run_query(graph_obj, query, {'events': buffers['flow']})
            buffers['flow'] = []

        if flow_only:
            # Clear other buffers without ingesting if in flow_only mode
            for k in buffers:
                if k != 'flow': buffers[k] = []
            return

        # 2. DNS Queries — aggregate per (src, hostname)
        if len(buffers['dns_query']) >= batch_size or (force and buffers['dns_query']):
            query = """
            UNWIND $events AS e
            MERGE (src:IPAddress {ip: e.src})
            ON CREATE SET src.name = e.src
            MERGE (hn:Hostname {name: e.hostname})
            MERGE (src)-[r:QUERIED_DNS]->(hn)
            ON CREATE SET r.count = 1,
                          r.first_seen = e.timestamp,
                          r.last_seen = e.timestamp,
                          r.resolver_ip = e.resolver
            ON MATCH SET  r.count = r.count + 1,
                          r.last_seen = e.timestamp
            """
            run_query(graph_obj, query, {'events': buffers['dns_query']})
            buffers['dns_query'] = []

        # 3. DNS Answers (already idempotent via MERGE)
        if len(buffers['dns_answer']) >= batch_size or (force and buffers['dns_answer']):
            query = """
            UNWIND $events AS e
            MERGE (hn:Hostname {name: e.hostname})
            MERGE (ip:IPAddress {ip: e.address})
            ON CREATE SET ip.name = e.address
            MERGE (hn)-[:RESOLVES_TO {resolver_ip: e.resolver}]->(ip)
            """
            run_query(graph_obj, query, {'events': buffers['dns_answer']})
            buffers['dns_answer'] = []

        # 4. HTTP / TLS / QUIC Hostname Observations — aggregate per (hn, dst, source)
        for source in ['http_request', 'tls_handshake', 'quic_event']:
            if len(buffers[source]) >= batch_size or (force and buffers[source]):
                label_map = {'http_request': 'http', 'tls_handshake': 'tls', 'quic_event': 'quic'}
                query = f"""
                UNWIND $events AS e
                MERGE (hn:Hostname {{name: e.hostname}})
                MERGE (dst:IPAddress {{ip: e.dest}})
                ON CREATE SET dst.name = e.dest
                MERGE (hn)-[r:OBSERVED_ON {{source: '{label_map[source]}'}}]->(dst)
                ON CREATE SET r.count = 1,
                              r.first_seen = e.timestamp,
                              r.last_seen = e.timestamp
                ON MATCH SET  r.count = r.count + 1,
                              r.last_seen = e.timestamp
                """
                run_query(graph_obj, query, {'events': buffers[source]})
                buffers[source] = []

        # 5. JA4 and Server Fingerprints
        if len(buffers['ja4']) >= batch_size or (force and buffers['ja4']):
            query = """
            UNWIND $events AS e
            MERGE (src:IPAddress {ip: e.src})
            ON CREATE SET src.name = e.src
            MERGE (fp:Fingerprint {id: e.ja4, type: 'ja4'})
            ON CREATE SET fp.name = e.ja4
            MERGE (src)-[r:USED_FINGERPRINT {context: 'tls'}]->(fp)
            ON CREATE SET r.count = 1,
                          r.first_seen = e.timestamp,
                          r.last_seen = e.timestamp
            ON MATCH SET  r.count = r.count + 1,
                          r.last_seen = e.timestamp
            
            // Associate JA4 with Hostname (SNI)
            WITH e, fp
            WHERE e.hostname IS NOT NULL
            MERGE (hn:Hostname {name: e.hostname})
            MERGE (fp)-[rel:ASSOCIATED_WITH]->(hn)
            ON CREATE SET rel.count = 1, rel.first_seen = e.timestamp, rel.last_seen = e.timestamp
            ON MATCH SET rel.count = rel.count + 1, rel.last_seen = e.timestamp

            // Associate Destination IP with Server Certificate Fingerprint
            WITH e
            WHERE e.server_fingerprint IS NOT NULL
            MERGE (sfp:Fingerprint {id: e.server_fingerprint, type: 'sha1_cert'})
            ON CREATE SET sfp.name = e.server_fingerprint
            MERGE (dst:IPAddress {ip: e.dest})
            ON CREATE SET dst.name = e.dest
            MERGE (dst)-[sr:PRESENTED_FINGERPRINT]->(sfp)
            ON CREATE SET sr.count = 1, sr.first_seen = e.timestamp, sr.last_seen = e.timestamp
            ON MATCH SET sr.count = sr.count + 1, sr.last_seen = e.timestamp
            """
            run_query(graph_obj, query, {'events': buffers['ja4']})
            buffers['ja4'] = []

    for file_path in suricata_files:
        print(f"Processing {file_path.name}...")
        file_count = 0
        for event in parse_suricata(file_path):
            etype = event['type']
            
            # If in flow_only mode, only buffer flows
            if flow_only and etype != 'flow':
                continue

            if etype in buffers:
                if etype == 'tls_handshake' and event.get('ja4'):
                    buffers['ja4'].append(event)
                
                if etype in ['http_request', 'tls_handshake', 'quic_event'] and not event.get('hostname'):
                    pass
                else:
                    buffers[etype].append(event)
            
            total_count += 1
            file_count += 1
            
            if total_count % batch_size == 0:
                flush_buffers(graph)
            
            if file_count % 50000 == 0:
                print(f"  Processed {file_count} events in {file_path.name}...")

    flush_buffers(graph, force=True)
    print(f"Suricata ingestion complete. Total events: {total_count}")

    if include_osquery and not flow_only:
        print("Ingesting OSQuery processes...")
        # ... (osquery logic remains same)
        osquery_file = DATA_DIR / 'osqueryd.results.log'
        if osquery_file.exists():
            proc_count = 0
            for proc in parse_osquery(osquery_file):
                query = """
                MERGE (h:Host {host_identifier: $host_id})
                ON CREATE SET h.name = $host_id
                MERGE (p:Process {name: $name, pid: $pid})
                ON CREATE SET p.path = $path
                MERGE (h)-[:RAN_PROCESS]->(p)
                """
                if proc.get('address') and proc['address'] not in ['0.0.0.0', '']:
                    query += """
                    MERGE (ip:IPAddress {ip: $address})
                    ON CREATE SET ip.name = $address
                    MERGE (p)-[:LISTENS_ON]->(ip)
                    MERGE (h)-[:HAS_IP]->(ip)
                    """
                graph.query(query, proc)
                proc_count += 1
    
    print("Ingestion Complete!")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-osquery", action="store_true")
    parser.add_argument("--flow-only", action="store_true", help="Only ingest 'flow' events to build network backbone.")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--limit", type=int, help="Limit the number of Suricata files to process.")
    parser.add_argument("--reset", action="store_true", help="Delete the existing graph before ingesting.")
    parser.add_argument("--start-from", type=str, help="Skip files before this filename (e.g. eve-2026-01-25-01.json).")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(
        include_osquery=args.include_osquery,
        flow_only=args.flow_only,
        batch_size=args.batch_size,
        limit=args.limit,
        reset=args.reset,
        start_from=args.start_from,
    )

// Correlate DNS queries and TLS handshakes that occurred very close in time for the same host
MATCH (src:IPAddress)-[dns:QUERIED_DNS]->(hn:Hostname)-[tls:OBSERVED_ON {source: 'tls'}]->(dst:IPAddress)
WHERE dns.last_seen IS NOT NULL AND tls.last_seen IS NOT NULL
  // Since timestamps are strings, we can't do math easily in pure Cypher, 
  // but we can identify which hosts show consistent sequences.
RETURN src.ip, hn.name, dst.ip, dns.last_seen as dns_time, tls.last_seen as tls_time
ORDER BY dns.last_seen DESC
LIMIT 50

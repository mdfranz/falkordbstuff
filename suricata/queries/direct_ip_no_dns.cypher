// External connections from internal hosts where no DNS resolution preceded the flow
MATCH (src:IPAddress) WHERE src.ip STARTS WITH '192.168.'
MATCH (src)-[f:NETWORK_FLOW]->(dst:IPAddress)
WHERE NOT dst.ip STARTS WITH '192.168.'
  AND NOT (src)-[:QUERIED_DNS]->(:Hostname)-[:RESOLVES_TO]->(dst)
  AND NOT (:Hostname)-[:OBSERVED_ON {source: 'tls'}]->(dst)
RETURN src.ip, dst.ip, f.proto, f.port, f.count, f.bytes_toserver
ORDER BY f.bytes_toserver DESC LIMIT 50

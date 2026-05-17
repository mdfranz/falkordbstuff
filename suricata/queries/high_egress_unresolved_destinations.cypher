// High egress flows to external destinations (broader companion to data_exfiltration.cypher)
MATCH (src:IPAddress)-[f:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.'
  AND NOT dst.ip STARTS WITH '192.168.'
  AND COALESCE(f.bytes_toserver, 0) > 750000
RETURN src.ip, dst.ip, f.proto, f.port, f.bytes_toserver, f.bytes_toclient, f.count
ORDER BY f.bytes_toserver DESC
LIMIT 50

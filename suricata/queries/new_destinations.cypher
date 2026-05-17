// Identify the newest external destinations (IPs seen for the first time recently)
MATCH (src:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.'
  AND NOT dst.ip STARTS WITH '192.168.'
RETURN dst.ip, r.first_seen as first_seen, r.proto as proto, r.port as port
ORDER BY r.first_seen DESC
LIMIT 20

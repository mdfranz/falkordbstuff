// Measure the "dwell time" or persistence of connections to external IPs
MATCH (src:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.'
  AND NOT dst.ip STARTS WITH '192.168.'
RETURN dst.ip, r.first_seen as first_seen, r.last_seen as last_seen, r.count as flow_count
ORDER BY r.first_seen ASC
LIMIT 50

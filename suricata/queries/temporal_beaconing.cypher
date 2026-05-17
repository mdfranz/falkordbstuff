// Identify potential beaconing behavior: High flow counts over a long period
MATCH (src:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.'
  AND NOT dst.ip STARTS WITH '192.168.'
  AND r.count > 100
RETURN src.ip, dst.ip, r.count, r.first_seen, r.last_seen
ORDER BY r.count DESC
LIMIT 50

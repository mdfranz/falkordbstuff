// Internal hosts communicating directly with other internal hosts
MATCH (src:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.' AND dst.ip STARTS WITH '192.168.'
RETURN src.ip, dst.ip, r.proto, r.port, r.count, r.bytes_toserver
ORDER BY r.count DESC

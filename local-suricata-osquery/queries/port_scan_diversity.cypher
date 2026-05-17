// Internal hosts connecting to an unusually large number of distinct destination ports —
// scanning or noisy application behavior
MATCH (src:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.'
WITH src, collect(DISTINCT r.port) AS ports
WHERE size(ports) > 10
RETURN src.ip, size(ports) AS port_count, ports
ORDER BY port_count DESC

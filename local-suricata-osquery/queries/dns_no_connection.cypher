// Internal hosts that queried many hostnames but never connected to the resolved IPs —
// possible reconnaissance or failed C2 beaconing
MATCH (src:IPAddress)-[:QUERIED_DNS]->(hn:Hostname)
WHERE NOT (src)-[:NETWORK_FLOW]->(:IPAddress)<-[:RESOLVES_TO]-(hn)
  AND src.ip STARTS WITH '192.168.'
WITH src, collect(hn.name) AS queried_never_connected
WHERE size(queried_never_connected) > 5
RETURN src.ip, size(queried_never_connected) AS count, queried_never_connected[..10] AS sample
ORDER BY count DESC LIMIT 20

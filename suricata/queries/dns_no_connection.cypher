// Internal hosts that queried many hostnames but never connected to the resolved IPs
MATCH (src:IPAddress) WHERE src.ip STARTS WITH '192.168.'
MATCH (src)-[:QUERIED_DNS]->(hn:Hostname)
WHERE NOT (src)-[:NETWORK_FLOW]->(:IPAddress)<-[:RESOLVES_TO]-(hn)
WITH src, collect(hn.name) AS queried_never_connected
WHERE size(queried_never_connected) > 5
RETURN src.ip, size(queried_never_connected) AS count, queried_never_connected[..10] AS sample
ORDER BY count DESC LIMIT 20

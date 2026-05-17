// For each active internal host, compare queried hostnames vs queried hostnames that resolved to reached IPs
MATCH (src:IPAddress)-[:QUERIED_DNS]->(hn_all:Hostname)
WHERE src.ip STARTS WITH '192.168.'
WITH src, count(DISTINCT hn_all) AS queried_hostnames
WHERE queried_hostnames >= 5
OPTIONAL MATCH (src)-[:NETWORK_FLOW]->(:IPAddress)<-[:RESOLVES_TO]-(hn_connected:Hostname)<-[:QUERIED_DNS]-(src)
WITH src, queried_hostnames, count(DISTINCT hn_connected) AS connected_hostnames
RETURN src.ip,
       queried_hostnames,
       connected_hostnames,
       (100.0 * connected_hostnames / queried_hostnames) AS conversion_pct
ORDER BY conversion_pct ASC, queried_hostnames DESC
LIMIT 50

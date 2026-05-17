// Find all hostnames associated with IP 192.168.3.133 via DNS or observation
MATCH (src:IPAddress {ip: '192.168.3.133'})-[:QUERIED_DNS]->(hn:Hostname)
RETURN 'DNS_QUERY' as type, hn.name as hostname, null as destination
UNION
MATCH (src:IPAddress {ip: '192.168.3.133'})-[f:NETWORK_FLOW]->(dst:IPAddress)
OPTIONAL MATCH (hn:Hostname)-[:OBSERVED_ON]->(dst)
WHERE hn IS NOT NULL
RETURN 'CONNECTION' as type, hn.name as hostname, dst.ip as destination
LIMIT 50
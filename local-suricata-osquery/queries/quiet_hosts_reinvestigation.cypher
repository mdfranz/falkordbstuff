// Find hosts with very few flows and check their DNS activity
MATCH (ip:IPAddress) WHERE ip.ip STARTS WITH '192.168.'
MATCH (ip)-[f:NETWORK_FLOW]->(dst:IPAddress)
WITH ip, f, dst
MATCH (ip)-[all_f:NETWORK_FLOW]-()
WITH ip, count(all_f) as total_flows, f, dst
WHERE total_flows < 5
OPTIONAL MATCH (ip)-[d:QUERIED_DNS]->()
RETURN ip.ip as host, total_flows, count(d) as dns_queries, f.proto as proto, dst.ip as destination, f.bytes_toserver as sent
ORDER BY total_flows ASC
LIMIT 50
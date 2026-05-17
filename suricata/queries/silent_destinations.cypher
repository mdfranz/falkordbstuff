// Optimized way to find silent hosts and their destinations
// Step 1: Find internal IPs with exactly 1 network flow
MATCH (ip:IPAddress) WHERE ip.ip STARTS WITH '192.168.'
MATCH (ip)-[f:NETWORK_FLOW]-()
WITH ip, count(f) as flow_count
WHERE flow_count = 1

// Step 2: Ensure they have no DNS activity
OPTIONAL MATCH (ip)-[d:QUERIED_DNS]->()
WITH ip, flow_count, count(d) as dns_count
WHERE dns_count = 0

// Step 3: Get their destination details
MATCH (ip)-[r:NETWORK_FLOW]->(dst:IPAddress)
RETURN ip.ip as silent_host, r.proto as proto, dst.ip as destination, r.bytes_toserver as sent
ORDER BY silent_host ASC
LIMIT 100
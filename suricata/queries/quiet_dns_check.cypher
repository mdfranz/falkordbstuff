// Check if any of the "quiet" hosts performed DNS queries
MATCH (ip:IPAddress)
WHERE ip.ip STARTS WITH '192.168.'
WITH ip
MATCH (ip)-[r:NETWORK_FLOW]-()
WITH ip, count(r) AS flow_count
WHERE flow_count = 1
OPTIONAL MATCH (ip)-[dns:QUERIED_DNS]->(hn:Hostname)
WITH ip, flow_count, count(dns) AS dns_count
ORDER BY dns_count ASC
LIMIT 20
RETURN ip.ip, flow_count, dns_count
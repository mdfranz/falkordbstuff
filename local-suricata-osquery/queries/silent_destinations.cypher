// Find where these "silent" hosts are connecting
MATCH (ip:IPAddress)
WHERE ip.ip STARTS WITH '192.168.'
WITH ip
MATCH (ip)-[r:NETWORK_FLOW]->(dst:IPAddress)
WITH ip, r, dst
MATCH (ip)-[all_f:NETWORK_FLOW]-()
WITH ip, r, dst, count(all_f) AS flow_count
WHERE flow_count = 1
OPTIONAL MATCH (ip)-[dns:QUERIED_DNS]->()
WITH ip, r, dst, count(dns) AS dns_count
WHERE dns_count = 0
RETURN ip.ip as silent_host, r.proto as proto, dst.ip as destination, r.bytes_toserver as sent
ORDER BY silent_host ASC
LIMIT 50
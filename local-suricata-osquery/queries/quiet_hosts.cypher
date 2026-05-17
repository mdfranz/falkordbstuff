// Identify internal hosts with the lowest number of flows
MATCH (ip:IPAddress)
WHERE ip.ip STARTS WITH '192.168.'
MATCH (ip)-[r:NETWORK_FLOW]-()
WITH ip, count(r) AS flow_count, sum(r.bytes_toserver) AS sent, sum(r.bytes_toclient) AS received
ORDER BY flow_count ASC
LIMIT 20
RETURN ip.ip, flow_count, sent, received
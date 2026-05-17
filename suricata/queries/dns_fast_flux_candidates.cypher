// Hostnames observed on many destination IPs (possible fast-flux/CDN churn)
MATCH (hn:Hostname)-[:OBSERVED_ON]->(ip:IPAddress)
WITH hn, collect(DISTINCT ip.ip) AS observed_ips
WITH hn, observed_ips, size(observed_ips) AS observed_ip_count
WHERE observed_ip_count >= 10
OPTIONAL MATCH (src:IPAddress)-[q:QUERIED_DNS]->(hn)
WHERE src.ip STARTS WITH '192.168.'
WITH hn, observed_ips, observed_ip_count, count(DISTINCT src) AS internal_hosts, sum(COALESCE(q.count, 1)) AS total_queries
RETURN hn.name, observed_ip_count, internal_hosts, COALESCE(total_queries, 0) AS total_queries, observed_ips[..10] AS sample_ips
ORDER BY observed_ip_count DESC, total_queries DESC
LIMIT 50

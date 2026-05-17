MATCH (ip:IPAddress)-[:PRESENTED_FINGERPRINT]->(fp:Fingerprint)
WITH fp, collect(DISTINCT ip.ip) AS ips, sum(ip.count) as total_seen
WHERE size(ips) > 1
RETURN fp.id, ips, size(ips) AS ip_count
ORDER BY ip_count DESC
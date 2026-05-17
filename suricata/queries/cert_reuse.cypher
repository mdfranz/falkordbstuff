// Certificate fingerprints presented by multiple destination IPs
MATCH (ip:IPAddress)-[r:PRESENTED_FINGERPRINT]->(fp:Fingerprint {type: 'sha1_cert'})
WITH fp, collect(DISTINCT ip.ip) AS ips, sum(COALESCE(r.count, 1)) AS total_presentations
WHERE size(ips) > 5
RETURN fp.id, size(ips) AS ip_count, total_presentations, ips[..10] AS sample_ips
ORDER BY ip_count DESC, total_presentations DESC
LIMIT 100

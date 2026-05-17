MATCH (ip:IPAddress)-[:PRESENTED_FINGERPRINT]->(fp:Fingerprint)
WITH ip, count(DISTINCT fp) AS cert_count
WHERE cert_count > 1
RETURN ip.ip, cert_count
ORDER BY cert_count DESC
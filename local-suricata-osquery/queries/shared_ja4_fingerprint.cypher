// Same JA4 TLS fingerprint used by multiple internal hosts — pivot for malware family identification
MATCH (src:IPAddress)-[:USED_FINGERPRINT]->(fp:Fingerprint {type: 'ja4'})
WHERE src.ip STARTS WITH '192.168.'
WITH fp, collect(DISTINCT src.ip) AS hosts
WHERE size(hosts) > 2
RETURN fp.id, size(hosts) AS host_count, hosts
ORDER BY host_count DESC

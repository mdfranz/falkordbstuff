// How widely shared are JA4 fingerprints used by 192.168.2.223
MATCH (:IPAddress {ip: '192.168.2.223'})-[:USED_FINGERPRINT {context: 'tls'}]->(fp:Fingerprint {type: 'ja4'})
MATCH (peer:IPAddress)-[:USED_FINGERPRINT {context: 'tls'}]->(fp)
WITH fp, count(DISTINCT peer) AS host_count
RETURN fp.id, host_count
ORDER BY host_count DESC
LIMIT 50

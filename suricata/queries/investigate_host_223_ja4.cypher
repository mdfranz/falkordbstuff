// JA4 fingerprints used by 192.168.2.223
MATCH (:IPAddress {ip: '192.168.2.223'})-[r:USED_FINGERPRINT {context: 'tls'}]->(fp:Fingerprint {type: 'ja4'})
RETURN fp.id, COALESCE(r.count, 1) AS uses, r.first_seen, r.last_seen
ORDER BY uses DESC
LIMIT 50

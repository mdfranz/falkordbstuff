MATCH (ip:IPAddress {ip: '13.107.213.40'})-[:PRESENTED_FINGERPRINT]->(fp:Fingerprint)
RETURN fp.id, fp.type, fp.name
ORDER BY fp.id
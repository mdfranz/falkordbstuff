// JA4 fingerprints associated with many TLS hostnames and destination IPs
MATCH (fp:Fingerprint {type: 'ja4'})-[:ASSOCIATED_WITH]->(hn:Hostname)-[:OBSERVED_ON {source: 'tls'}]->(dst:IPAddress)
WITH fp, collect(DISTINCT hn.name) AS snis, collect(DISTINCT dst.ip) AS destinations
WHERE size(snis) >= 5
  AND size(destinations) >= 8
RETURN fp.id, size(snis) AS sni_count, size(destinations) AS destination_count, snis[..8] AS sample_snis, destinations[..8] AS sample_destinations
ORDER BY destination_count DESC, sni_count DESC
LIMIT 50

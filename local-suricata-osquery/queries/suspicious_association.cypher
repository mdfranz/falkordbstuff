MATCH (fp:Fingerprint {type: 'ja4'})-[r:ASSOCIATED_WITH]->(hn:Hostname)
WHERE hn.name CONTAINS 'google' OR hn.name CONTAINS 'adobe'
WITH hn, fp, r.count as count
ORDER BY hn.name, count DESC
RETURN hn.name, collect({fp: fp.id, seen: count})[1..] AS anomalies
MATCH (fp:Fingerprint {type: 'ja4'})-[r:ASSOCIATED_WITH]->(hn:Hostname)
RETURN fp.id, count(DISTINCT hn.name) AS unique_snis, sum(r.count) AS total_uses
ORDER BY unique_snis DESC
LIMIT 10
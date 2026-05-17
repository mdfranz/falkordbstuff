// Internal hosts using unusually many DNS resolvers
MATCH (src:IPAddress)-[q:QUERIED_DNS]->(:Hostname)
WHERE src.ip STARTS WITH '192.168.'
  AND q.resolver_ip IS NOT NULL
WITH src, collect(DISTINCT q.resolver_ip) AS resolvers, sum(COALESCE(q.count, 1)) AS total_queries
WHERE size(resolvers) > 2
RETURN src.ip, size(resolvers) AS resolver_count, total_queries, resolvers[..10] AS sample_resolvers
ORDER BY resolver_count DESC, total_queries DESC
LIMIT 50

// Resolver IPs used by 192.168.2.223, ranked by volume
MATCH (:IPAddress {ip: '192.168.2.223'})-[q:QUERIED_DNS]->(hn:Hostname)
WHERE q.resolver_ip IS NOT NULL
WITH q.resolver_ip AS resolver_ip,
     count(DISTINCT hn) AS unique_hostnames,
     sum(COALESCE(q.count, 1)) AS query_events
RETURN resolver_ip, unique_hostnames, query_events
ORDER BY query_events DESC, unique_hostnames DESC
LIMIT 100

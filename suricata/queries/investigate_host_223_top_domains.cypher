// Top queried hostnames from 192.168.2.223 with associated resolver IP
MATCH (:IPAddress {ip: '192.168.2.223'})-[q:QUERIED_DNS]->(hn:Hostname)
WITH hn.name AS hostname,
     q.resolver_ip AS resolver_ip,
     COALESCE(q.count, 1) AS query_events,
     q.first_seen AS first_seen,
     q.last_seen AS last_seen
RETURN hostname, resolver_ip, query_events, first_seen, last_seen
ORDER BY query_events DESC
LIMIT 100

// High-level DNS and flow summary for 192.168.2.223
MATCH (:IPAddress {ip: '192.168.2.223'})-[q:QUERIED_DNS]->(:Hostname)
WITH count(DISTINCT q.resolver_ip) AS distinct_resolvers,
     count(*) AS dns_relationships,
     sum(COALESCE(q.count, 1)) AS total_dns_query_events
MATCH (:IPAddress {ip: '192.168.2.223'})-[f:NETWORK_FLOW]->(:IPAddress)
RETURN distinct_resolvers,
       dns_relationships,
       total_dns_query_events,
       count(*) AS flow_relationships,
       sum(COALESCE(f.count, 1)) AS total_flow_events,
       sum(COALESCE(f.bytes_toserver, 0)) AS total_bytes_out,
       sum(COALESCE(f.bytes_toclient, 0)) AS total_bytes_in

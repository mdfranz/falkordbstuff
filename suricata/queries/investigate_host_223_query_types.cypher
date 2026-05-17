// DNS query type profile for 192.168.2.223
MATCH (:IPAddress {ip: '192.168.2.223'})-[q:QUERIED_DNS]->(hn:Hostname)
WITH CASE
       WHEN hn.name ENDS WITH 'in-addr.arpa' THEN 'PTR_IPV4'
       WHEN hn.name ENDS WITH 'ip6.arpa' THEN 'PTR_IPV6'
       WHEN hn.name STARTS WITH '_' THEN 'SRV_OR_SPECIAL'
       ELSE 'FQDN'
     END AS query_type,
     count(DISTINCT hn) AS unique_names,
     sum(COALESCE(q.count, 1)) AS query_events
RETURN query_type, unique_names, query_events
ORDER BY query_events DESC

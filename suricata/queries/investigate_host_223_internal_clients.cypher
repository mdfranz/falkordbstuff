// Internal hosts sending likely DNS traffic to 192.168.2.223
MATCH (client:IPAddress)-[f:NETWORK_FLOW]->(:IPAddress {ip: '192.168.2.223'})
WHERE client.ip STARTS WITH '192.168.'
  AND f.port IN [53, 5353, 853]
RETURN client.ip, f.proto, f.port, COALESCE(f.count, 1) AS flow_events, COALESCE(f.bytes_toserver, 0) AS bytes_out
ORDER BY flow_events DESC
LIMIT 100

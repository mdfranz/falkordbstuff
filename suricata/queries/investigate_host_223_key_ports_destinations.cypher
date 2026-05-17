// Destinations contacted by 192.168.2.223 on key ports
MATCH (:IPAddress {ip: '192.168.2.223'})-[f:NETWORK_FLOW]->(dst:IPAddress)
WHERE f.port IN [53, 443, 3478, 5351, 1900]
RETURN dst.ip, f.proto, f.port, COALESCE(f.count, 1) AS flow_events, COALESCE(f.bytes_toserver, 0) AS bytes_out, COALESCE(f.bytes_toclient, 0) AS bytes_in
ORDER BY flow_events DESC
LIMIT 100

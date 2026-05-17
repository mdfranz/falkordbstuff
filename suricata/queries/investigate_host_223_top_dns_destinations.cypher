// Top DNS destinations (port 53) contacted by 192.168.2.223
MATCH (:IPAddress {ip: '192.168.2.223'})-[f:NETWORK_FLOW]->(dst:IPAddress)
WHERE f.port = 53
RETURN dst.ip, f.proto, COALESCE(f.count, 1) AS flow_events, COALESCE(f.bytes_toserver, 0) AS bytes_out, COALESCE(f.bytes_toclient, 0) AS bytes_in
ORDER BY flow_events DESC
LIMIT 100

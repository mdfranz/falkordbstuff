// Outbound flow profile of 192.168.2.223 by protocol/port
MATCH (:IPAddress {ip: '192.168.2.223'})-[f:NETWORK_FLOW]->(dst:IPAddress)
WITH f.proto AS proto,
     f.port AS port,
     count(DISTINCT dst) AS distinct_destinations,
     sum(COALESCE(f.count, 1)) AS flow_events,
     sum(COALESCE(f.bytes_toserver, 0)) AS bytes_out,
     sum(COALESCE(f.bytes_toclient, 0)) AS bytes_in
RETURN proto, port, distinct_destinations, flow_events, bytes_out, bytes_in
ORDER BY flow_events DESC, distinct_destinations DESC
LIMIT 50

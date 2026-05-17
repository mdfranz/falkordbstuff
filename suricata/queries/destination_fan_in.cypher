// External destinations contacted by many internal hosts
MATCH (src:IPAddress)-[f:NETWORK_FLOW]->(dst:IPAddress)
WHERE src.ip STARTS WITH '192.168.'
  AND NOT dst.ip STARTS WITH '192.168.'
WITH dst, collect(DISTINCT src.ip) AS internal_sources, sum(COALESCE(f.bytes_toserver, 0)) AS total_bytes_out, sum(COALESCE(f.count, 1)) AS total_flow_events
WHERE size(internal_sources) >= 10
OPTIONAL MATCH (:Hostname)-[o:OBSERVED_ON]->(dst)
WITH dst, internal_sources, total_bytes_out, total_flow_events, collect(DISTINCT o.source) AS observed_sources
RETURN dst.ip, size(internal_sources) AS internal_host_count, total_flow_events, total_bytes_out, observed_sources
ORDER BY internal_host_count DESC, total_bytes_out DESC
LIMIT 50

MATCH (src:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress)
WHERE r.bytes_toserver > (r.bytes_toclient * 10)
  AND r.bytes_toserver > 1000000
RETURN src.ip, dst.ip, r.bytes_toserver, r.bytes_toclient, r.proto
ORDER BY r.bytes_toserver DESC
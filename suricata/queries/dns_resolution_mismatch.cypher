// Hostnames where the DNS-resolved IP differs from the IP the connection was observed on —
// potential DNS spoofing, CDN bypass, or split-horizon DNS
MATCH (hn:Hostname)-[:RESOLVES_TO]->(resolved:IPAddress)
MATCH (hn)-[:OBSERVED_ON]->(observed:IPAddress)
WHERE resolved.ip <> observed.ip
RETURN hn.name, resolved.ip AS dns_answer, observed.ip AS actual_connection
LIMIT 50

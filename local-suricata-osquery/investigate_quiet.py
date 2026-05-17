from falkordb import FalkorDB
from prettytable import PrettyTable

ips = [
    '192.168.1.218', '192.168.0.163', '192.168.12.190', '192.168.68.70', 
    '192.168.1.239', '192.168.1.192', '192.168.1.157', '192.168.1.236', 
    '192.168.2.223', '192.168.0.2', '192.168.1.182', '192.168.66.1', 
    '192.168.0.48', '192.168.10.136', '192.168.1.45', '192.168.1.77', 
    '192.168.0.31', '192.168.0.93', '192.168.50.66', '192.168.0.171'
]

db = FalkorDB(host='localhost', port=6379)
graph = db.select_graph('suricata')

query = "MATCH (ip:IPAddress)-[r:NETWORK_FLOW]->(dst:IPAddress) WHERE ip.ip IN $ips RETURN ip.ip, r.proto, dst.ip, r.bytes_toserver"
result = graph.query(query, {'ips': ips})

table = PrettyTable(['Host', 'Proto', 'Destination', 'Sent'])
for row in result.result_set:
    table.add_row(row)

print(table)

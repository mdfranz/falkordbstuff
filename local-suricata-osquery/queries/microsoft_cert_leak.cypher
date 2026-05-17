MATCH (ip:IPAddress)-[:PRESENTED_FINGERPRINT]->(fp:Fingerprint)
WHERE fp.id IN [
  '07:a4:03:54:fb:d3:7a:70:e7:91:88:7c:bd:52:b2:8c:0e:c4:b7:33',
  '16:01:4d:2a:59:9d:5b:f5:2a:23:5e:d5:3d:a0:4a:60:bb:ae:c8:b5',
  '27:32:47:3a:f4:fb:3e:78:a3:47:c9:ba:07:70:89:f4:91:ea:27:47',
  '27:e4:00:0c:a6:a0:7b:ea:99:9b:43:2f:75:e5:14:e6:f3:06:17:68',
  '4b:60:b0:7a:e3:cc:62:28:06:67:4b:91:aa:9e:14:4e:97:d4:f2:e5',
  '64:72:8f:99:76:c4:04:9e:7d:34:f9:47:12:11:b4:bf:0c:b4:54:c1'
]
AND NOT ip.ip STARTS WITH '13.107.'
RETURN ip.ip, fp.id
ORDER BY ip.ip
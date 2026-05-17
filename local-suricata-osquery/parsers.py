import json
from ipaddress import ip_address


def is_ipv4(address):
    if not address:
        return False
    try:
        return ip_address(address).version == 4
    except ValueError:
        return False


def is_routable_ipv4(address):
    if not address:
        return False
    try:
        ip = ip_address(address)
    except ValueError:
        return False
    if ip.version != 4:
        return False
    if ip.is_multicast or ip.is_unspecified or ip.is_reserved:
        return False
    if address == "255.255.255.255":
        return False
    return True


def normalize_hostname(value):
    if not value:
        return None

    # Strip null bytes and non-printable characters that can break the DB parser
    value = "".join(c for c in value if c.isprintable() and c != "\x00")
    
    hostname = value.strip().rstrip(".").lower()
    if not hostname or is_ipv4(hostname):
        return None
    return hostname

def parse_suricata(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                src_ip = event.get('src_ip')
                dest_ip = event.get('dest_ip')
                
                # Filter to routable IPv4 (drop multicast, broadcast, reserved)
                if not is_routable_ipv4(src_ip) or not is_routable_ipv4(dest_ip):
                    continue

                event_type = event.get('event_type')
                
                if event_type == 'flow':
                    flow_data = event.get('flow', {})
                    yield {
                        'type': 'flow',
                        'src': src_ip,
                        'dest': dest_ip,
                        'timestamp': event.get('timestamp'),
                        'proto': event.get('proto'),
                        'bytes_toserver': flow_data.get('bytes_toserver'),
                        'bytes_toclient': flow_data.get('bytes_toclient')
                    }
                elif event_type == 'dns':
                    dns = event.get('dns', {})
                    dns_type = dns.get('type')
                    # Suricata emits legacy 'query'/'answer' or v3 'request'/'response'
                    if dns_type in ('query', 'request'):
                        # v3 puts the name in queries[]; legacy puts it at top level
                        rrname = dns.get('rrname')
                        if not rrname:
                            queries = dns.get('queries') or []
                            if queries:
                                rrname = queries[0].get('rrname')
                        hostname = normalize_hostname(rrname)
                        if not hostname:
                            continue
                        yield {
                            'type': 'dns_query',
                            'src': src_ip,
                            'resolver': dest_ip,
                            'hostname': hostname,
                            'timestamp': event.get('timestamp')
                        }
                    elif dns_type in ('answer', 'response'):
                        rrname = dns.get('rrname')
                        if not rrname:
                            queries = dns.get('queries') or []
                            if queries:
                                rrname = queries[0].get('rrname')
                        hostname = normalize_hostname(rrname)
                        if not hostname:
                            continue

                        answers = []
                        for answer in dns.get('answers', []):
                            if answer.get('rrtype') == 'A' and is_routable_ipv4(answer.get('rdata')):
                                answers.append(answer['rdata'])

                        if not answers:
                            answers = [
                                addr for addr in dns.get('grouped', {}).get('A', [])
                                if is_routable_ipv4(addr)
                            ]

                        for answer_ip in answers:
                            yield {
                                'type': 'dns_answer',
                                'hostname': hostname,
                                'address': answer_ip,
                                'resolver': src_ip,
                                'timestamp': event.get('timestamp')
                            }
                elif event_type == 'http':
                    http = event.get('http', {})
                    yield {
                        'type': 'http_request',
                        'src': src_ip,
                        'dest': dest_ip,
                        'hostname': normalize_hostname(http.get('hostname')),
                        'url': http.get('url'),
                        'timestamp': event.get('timestamp')
                    }
                elif event_type == 'tls':
                    tls = event.get('tls', {})
                    yield {
                        'type': 'tls_handshake',
                        'src': src_ip,
                        'dest': dest_ip,
                        'hostname': normalize_hostname(tls.get('sni')),
                        'version': tls.get('version'),
                        'ja4': tls.get('ja4'),
                        'server_fingerprint': tls.get('fingerprint'),
                        'timestamp': event.get('timestamp')
                    }
                elif event_type == 'quic':
                    quic = event.get('quic', {})
                    yield {
                        'type': 'quic_event',
                        'src': src_ip,
                        'dest': dest_ip,
                        'hostname': normalize_hostname(quic.get('sni')),
                        'version': quic.get('version'),
                        'timestamp': event.get('timestamp')
                    }
            except json.JSONDecodeError:
                continue

def parse_osquery(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                name = event.get('name')
                host_id = event.get('hostIdentifier')
                columns = event.get('columns', {})
                address = columns.get('address')
                
                # Filter for IPv4 only
                if address and not is_ipv4(address):
                    continue

                if name == 'active_processes':
                    yield {
                        'type': 'process',
                        'host_id': host_id,
                        'pid': int(columns.get('pid', 0)),
                        'name': columns.get('name'),
                        'path': columns.get('path'),
                        'address': address
                    }
            except json.JSONDecodeError:
                continue

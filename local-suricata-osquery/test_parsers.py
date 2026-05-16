from parsers import parse_suricata, parse_osquery
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

def test_suricata_parser():
    print("Testing Suricata parser...")
    events = list(parse_suricata(DATA_DIR / 'eve.json'))
    assert len(events) > 0

    flow_count = sum(1 for event in events if event['type'] == 'flow')
    dns_answer_count = sum(1 for event in events if event['type'] == 'dns_answer')
    bad_hostnames = [
        event for event in events
        if event.get('hostname') and event['hostname'].count('.') == 3 and event['hostname'].replace('.', '').isdigit()
    ]

    assert flow_count > 0
    assert dns_answer_count > 0
    assert not bad_hostnames
    print(f"Parsed {len(events)} Suricata events. First event: {events[0]}")

def test_osquery_parser():
    print("Testing OSQuery parser...")
    osquery_path = DATA_DIR / 'osqueryd.results.log'
    if osquery_path.exists():
        procs = list(parse_osquery(osquery_path))
        assert len(procs) > 0
        print(f"Parsed {len(procs)} processes. First process: {procs[0]}")
    else:
        print("data/osqueryd.results.log not found, skipping test.")

if __name__ == "__main__":
    try:
        test_suricata_parser()
        test_osquery_parser()
        print("Parser tests passed!")
    except Exception as e:
        print(f"Parser tests failed: {e}")

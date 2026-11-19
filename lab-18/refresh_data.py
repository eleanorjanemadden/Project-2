"""Download and run COST/JPM. Optional DNS fallback is for this workspace's missing resolver."""
import argparse
import json
from pathlib import Path
import socket
import sys

import requests

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'skill/buffett-sec/scripts'))
from buffett import download, report, screen


def enable_dns_fallback():
    """Resolve hostnames over HTTPS only after OS DNS fails; TLS verification stays on."""
    original = socket.getaddrinfo
    cache = {}
    def resolve(host, port, *args, **kwargs):
        try:
            return original(host, port, *args, **kwargs)
        except socket.gaierror:
            if host not in cache:
                response = requests.get('https://1.1.1.1/dns-query',
                                        params={'name': host, 'type': 'A'},
                                        headers={'accept': 'application/dns-json'}, timeout=15)
                response.raise_for_status()
                cache[host] = next(a['data'] for a in response.json()['Answer'] if a['type'] == 1)
            return original(cache[host], port, *args, **kwargs)
    socket.getaddrinfo = resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dns-fallback', action='store_true')
    args = parser.parse_args()
    if args.dns_fallback:
        enable_dns_fallback()
    for ticker in ['COST', 'JPM']:
        result = screen(download(ticker, ROOT / 'data'), ticker)
        (ROOT / 'outputs' / f'{ticker}_results.json').write_text(json.dumps(result, indent=2)+'\n')
        text = report(result)
        (ROOT / 'outputs' / f'{ticker}_run.txt').write_text(text)
        print(text)


if __name__ == '__main__':
    main()

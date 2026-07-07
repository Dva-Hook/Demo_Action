#!/usr/bin/env python3
"""Quick proxy tester. Usage:
    python test_proxy.py socks5://host:port:user:pass
    python test_proxy.py host:port:user:pass
    python test_proxy.py host:port
"""

import sys, socket, struct, base64
import requests as _req

def parse(line):
    """Returns (protocol, host, port, user, pwd) or None."""
    line = line.strip()
    if not line: return None
    protocol = 'http'
    if '://' in line:
        protocol, line = line.split('://', 1)
    parts = line.split(':')
    if len(parts) == 2:
        host, port = parts
        try: int(port)
        except ValueError: print(f'[FAIL] Invalid port: {line}'); return None
        return (protocol, host, port, None, None)
    elif len(parts) == 4:
        host, port, user, pwd = parts
        try: int(port)
        except ValueError: print(f'[FAIL] Invalid port: {line}'); return None
        return (protocol, host, port, user, pwd)
    else:
        print(f'[FAIL] Expected [protocol://]host:port[:user:pass], got: {line}')
        return None

def test_direct():
    """Test direct connection (no proxy)."""
    print('--- Direct (no proxy) ---')
    try:
        r = _req.get('http://httpbin.org/ip', timeout=8)
        ip = r.json().get('origin', 'unknown')
        print(f'[OK]   Exit IP: {ip}')
        return True
    except Exception as e:
        print(f'[FAIL] {e}')
        return False

def test_http(host, port, user, pwd):
    """Test HTTP CONNECT proxy."""
    print(f'--- HTTP proxy: {host}:{port} ---')
    try:
        if user and pwd:
            proxy_url = f'http://{user}:{pwd}@{host}:{port}'
        else:
            proxy_url = f'http://{host}:{port}'
        r = _req.get('http://httpbin.org/ip',
                     proxies={'http': proxy_url, 'https': proxy_url},
                     timeout=10)
        ip = r.json().get('origin', 'unknown')
        print(f'[OK]   Exit IP: {ip}')
        return True
    except Exception as e:
        print(f'[FAIL] {e}')
        return False

def test_socks5_raw(host, port, user, pwd, target_host='httpbin.org', target_port=80):
    """Raw SOCKS5 handshake test with detailed step logging."""
    print(f'--- SOCKS5 raw: {host}:{port} -> {target_host}:{target_port} ---')
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        print(f'[STEP1] Connecting to {host}:{port} ...')
        s.connect((host, int(port)))
        print(f'[OK]    TCP connected')

        # Greeting: version 5, 1 method, method 0x02 = user/pass
        s.sendall(b'\x05\x01\x02')
        resp = s.recv(2)
        print(f'[STEP2] Greeting response: {resp.hex()}')
        if resp != b'\x05\x02':
            print(f'[FAIL]  Proxy does not support user/pass auth (expected 0502, got {resp.hex()})')
            return False

        # Auth: version 1, user_len, user, pass_len, pass
        u, p = user.encode(), pwd.encode()
        auth_req = b'\x01' + bytes([len(u)]) + u + bytes([len(p)]) + p
        s.sendall(auth_req)
        resp = s.recv(2)
        print(f'[STEP3] Auth response: {resp.hex()}')
        if resp != b'\x01\x00':
            print(f'[FAIL]  Authentication rejected (expected 0100, got {resp.hex()})')
            return False
        print(f'[OK]    Authentication accepted')

        # Connect request
        ip_bytes = socket.inet_aton(socket.gethostbyname(target_host))
        req = b'\x05\x01\x00\x01' + ip_bytes + struct.pack('>H', target_port)
        s.sendall(req)
        resp = s.recv(10)
        print(f'[STEP4] Connect response: {resp.hex()}')
        if len(resp) < 10 or resp[1] != 0x00:
            print(f'[FAIL]  CONNECT to {target_host}:{target_port} rejected (code={resp[1] if len(resp) >= 2 else "?"})')
            return False
        print(f'[OK]    Tunnel to {target_host}:{target_port} established')

        # Send HTTP request through the tunnel
        http_req = f'GET /ip HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n'.encode()
        s.sendall(http_req)
        resp = b''
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            resp += chunk
        print(f'[STEP5] HTTP response length: {len(resp)} bytes')
        body_start = resp.find(b'\r\n\r\n')
        if body_start >= 0:
            import json
            body = json.loads(resp[body_start+4:].decode())
            print(f'[OK]    Exit IP: {body.get("origin", "unknown")}')
        else:
            print(f'[WARN]  Could not parse HTTP response')
        return True
    except Exception as e:
        print(f'[FAIL]  {type(e).__name__}: {e}')
        return False
    finally:
        if s:
            try: s.close()
            except: pass

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    raw = sys.argv[1]
    parsed = parse(raw)
    if not parsed:
        sys.exit(1)

    protocol, host, port, user, pwd = parsed
    print(f'Parsed: protocol={protocol} host={host} port={port} user={user} pwd={pwd}')
    print()

    results = {}

    # Test 1: direct
    results['direct'] = test_direct()
    print()

    # Test 2: HTTP CONNECT
    results['http'] = test_http(host, port, user, pwd)
    print()

    # Test 3: SOCKS5 raw
    if user and pwd:
        results['socks5'] = test_socks5_raw(host, port, user, pwd)
    else:
        results['socks5'] = test_socks5_raw(host, port, 'anonymous', 'anonymous')
    print()

    # Summary
    print('=' * 50)
    for name, ok in results.items():
        status = '[OK]' if ok else '[FAIL]'
        print(f'{status}  {name}')

if __name__ == '__main__':
    main()

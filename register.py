import string, time, random, logging, os, re, json, threading, socket, subprocess, atexit
from urllib.parse import unquote
from typing import Optional
from dataclasses import dataclass
import requests as _req
import websocket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger('battle_net')

REGISTER_URL = 'https://account.battle.net/creation/flow/creation-full'
COUNTRY = 'GBR'
BATTLE_TAG_BASE = 'Amireux'
CDP_DEBUG_PORT = 9222
CAPMONSTER_API_KEY = os.environ.get('CAPMONSTER_API_KEY', '')
IMPLICIT_WAIT_SEC = 8

# Anti-fingerprinting script injected via CDP before page load
STEALTH_JS = """(function() {
    'use strict';
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    const plugins = [
        {name:'Chrome PDF Plugin', filename:'internal-pdf-viewer', description:'Portable Document Format'},
        {name:'Chrome PDF Viewer', filename:'mhjfbmdgcfjbbpaeojofohoefgiehjai', description:''},
        {name:'Native Client', filename:'internal-nacl-plugin', description:''}];
    const fakePlugins = Object.setPrototypeOf(plugins, PluginArray.prototype);
    fakePlugins.item = i => plugins[i] || null;
    fakePlugins.namedItem = name => plugins.find(p => p.name === name) || null;
    fakePlugins.refresh = () => {};
    const mimeData = [
        {type:'application/pdf', suffixes:'pdf', plugin:fakePlugins[0]},
        {type:'text/pdf', suffixes:'pdf', plugin:fakePlugins[0]},
        {type:'application/x-nacl', suffixes:'', plugin:fakePlugins[2]},
        {type:'application/x-pnacl', suffixes:'', plugin:fakePlugins[2]}];
    const mimeTypes = Object.setPrototypeOf(mimeData.map(d => {
        const mt = Object.create(MimeType.prototype);
        mt.type = d.type; mt.suffixes = d.suffixes; mt.enabledPlugin = d.plugin;
        return mt;
    }), MimeTypeArray.prototype);
    mimeTypes.item = i => mimeData[i] ? mimeTypes[i] : null;
    mimeTypes.namedItem = name => mimeTypes.find(m => m.type === name) || null;
    const origPD = Object.getOwnPropertyDescriptor(Navigator.prototype, 'plugins');
    const origMD = Object.getOwnPropertyDescriptor(Navigator.prototype, 'mimeTypes');
    if (origPD) Object.defineProperty(Navigator.prototype, 'plugins', {get: () => fakePlugins});
    else Object.defineProperty(navigator, 'plugins', {get: () => fakePlugins});
    if (origMD) Object.defineProperty(Navigator.prototype, 'mimeTypes', {get: () => mimeTypes});
    const getParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(p) {
        if (p === 37445) return 'Intel Inc.';
        if (p === 37446) return 'Intel Iris OpenGL Engine';
        return getParam.call(this, p);
    };
    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
    if (!window.chrome) window.chrome = {};
    if (!window.chrome.runtime) window.chrome.runtime = {};
    if (!window.chrome.loadTimes) window.chrome.loadTimes = () => ({
        requestTime: Date.now()/1000, startLoadTime: Date.now()/1000, commitLoadTime: Date.now()/1000,
        finishDocumentLoadTime: Date.now()/1000, finishLoadTime: Date.now()/1000,
        firstPaintTime: Date.now()/1000-0.1, firstPaintAfterLoadTime: Date.now()/1000,
        navigationType: 'Other', wasFetchedViaSpdy: true, wasNpnNegotiated: true,
        npnNegotiatedProtocol: 'h2', wasAlternateProtocolAvailable: false, connectionInfo: 'h2'});
    if (!window.chrome.csi) window.chrome.csi = () => ({startE: Date.now(), onloadT: Date.now(), pageT: Math.random()*100+50, tran: 15});
    if (!window.chrome.app) window.chrome.app = {};
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {
        const ctx = this.getContext('2d');
        if (ctx) { const id = ctx.getImageData(0, 0, 2, 2); if (id && id.data.length > 10) { id.data[0] ^= 1; ctx.putImageData(id, 0, 0); } }
        return origToDataURL.apply(this, arguments);
    };
    const origQuery = navigator.permissions.query;
    navigator.permissions.query = function(params) {
        if (params.name === 'notifications') return Promise.resolve({state: Notification.permission, onchange: null});
        return origQuery.call(this, params);
    };
    Object.defineProperty(screen, 'colorDepth', {get: () => 24});
    Object.defineProperty(screen, 'pixelDepth', {get: () => 24});
    delete window.callPhantom;
    delete window._phantom;
    delete window.__nightmare;
})();"""

FIRST_NAMES = ['Natha','Narin','Nan','Nahon','Nafeh','Naira','Nina','Myie','Myle','Minh','Musa','Mogan','Monia','Demris','Delnn','Deler','Deisi','Dera','Decon','Dayan','Aziah','Ayy','Avia','Anti','Akibi']
LAST_NAMES = ['MEEZ','BUS','VGHN','PKS','DASON','SANO','NORIS','LOVE','SEE','CURY','PWERS','SCTZ','BAKER','GUAN','PAGE','MUZ','BAL','BBS','TER','GSS','FTZGD','STES','DOYLE','SHERN','SAURS','WSE','CON','GIL','ALO','GRER','PALA','SON','WATS','NUNZ','BOOE','COEZ']
MONTHS = ['01','02','03','04','05','06','07','08','09','10','11','12']
LETTERS_A_M = 'abcdefghijklm'
LETTERS_N_Z = 'nopqrstuvwxyz'

def random_pick(chars, count=1):
    return ''.join(random.choice(chars) for _ in range(count))
def random_digits(count=1):
    return random_pick(string.digits, count)
def generate_identity():
    first = random.choice(FIRST_NAMES); last = random.choice(LAST_NAMES)
    email_local = (last.lower() + random_pick(LETTERS_N_Z) + random_digits(2)
                 + first.lower() + random_digits(1) + random_pick(LETTERS_A_M) + random_pick(LETTERS_N_Z))
    return {
        'first_name': first.lower(), 'last_name': last.lower(),
        'email': f'{email_local}@outlook.com', 'password': email_local,
        'birth_year': str(random.randint(1970, 2000)),
        'birth_month': random.choice(MONTHS),
        'birth_day': str(random.randint(10, 28)),
        'battle_tag': f'{BATTLE_TAG_BASE}{random_digits(2)}',
    }

# ═══════════════════════════════ 代理工具 ═══════════════════════════════
def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def _parse_proxy_line(line):
    """Parse proxy line. Returns (protocol, host, port, user, pwd) or None. Default protocol is http."""
    line = line.strip()
    if not line: return None
    # Detect protocol prefix: socks5:// https:// http://
    protocol = 'http'
    if '://' in line:
        protocol, line = line.split('://', 1)
    parts = line.split(':')
    if len(parts) == 2:
        host, port = parts
        try: int(port)
        except ValueError: logger.warning(f'Invalid proxy port: {line}'); return None
        return (protocol, host, port, None, None)
    elif len(parts) == 4:
        host, port, user, pwd = parts
        try: int(port)
        except ValueError: logger.warning(f'Invalid proxy port: {line}'); return None
        return (protocol, host, port, user, pwd)
    else:
        logger.warning(f'Invalid proxy format (expected [protocol://]host:port[:user:pass]): {line}')
        return None

_proxy_processes = []
atexit.register(lambda: [p.kill() if hasattr(p, 'poll') else setattr(p, '_running', False) for p in _proxy_processes])

def _start_local_proxy(proxy_tuple, timeout=8):
    """Start local TCP forwarder: Chrome -> localhost:PORT -> upstream proxy (HTTP or SOCKS5).
    Returns (local_port, thread) or (None, None)."""
    protocol, host, port, user, pwd = proxy_tuple
    local_port = _find_free_port()

    import select as _sel

    def _socks5_connect(target_host, target_port):
        """Raw SOCKS5 handshake with username/password auth. Returns connected socket or raises."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((host, int(port)))
        # Greeting
        s.sendall(b"\x05\x01\x02")
        resp = s.recv(2)
        if resp != b"\x05\x02":
            raise Exception(f"SOCKS5 auth method rejected: {resp.hex()}")
        # Auth
        u, p = user.encode(), pwd.encode()
        s.sendall(b"\x01" + bytes([len(u)]) + u + bytes([len(p)]) + p)
        resp = s.recv(2)
        if resp != b"\x01\x00":
            raise Exception(f"SOCKS5 auth failed: {resp.hex()}")
        # Connect request
        import struct as _struct
        ip_bytes = socket.inet_aton(socket.gethostbyname(target_host))
        req = b"\x05\x01\x00\x01" + ip_bytes + _struct.pack(">H", target_port)
        s.sendall(req)
        resp = s.recv(10)
        if len(resp) < 10 or resp[1] != 0x00:
            raise Exception(f"SOCKS5 connect failed: {resp.hex() if len(resp) >= 2 else 'short'}")
        s.settimeout(None)
        return s

    def _http_connect(target_host, target_port):
        """HTTP CONNECT through upstream HTTP proxy with Basic auth. Returns connected socket."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((host, int(port)))
        import base64 as _b64
        cred = _b64.b64encode(f"{user}:{pwd}".encode()).decode()
        connect_req = (
            f"CONNECT {target_host}:{target_port} HTTP/1.1\r\n"
            f"Host: {target_host}:{target_port}\r\n"
            f"Proxy-Authorization: Basic {cred}\r\n"
            f"\r\n"
        ).encode()
        s.sendall(connect_req)
        resp = s.recv(4096)
        if not resp.startswith(b"HTTP/1.") or b"200" not in resp.split(b"\r\n")[0]:
            raise Exception(f"HTTP CONNECT failed: {resp.split(b'\r\n')[0].decode()}")
        s.settimeout(None)
        return s

    def _forward_pair(a, b):
        """Bidirectional byte forwarding between two sockets."""
        sockets = [a, b]
        while True:
            try:
                r, _, _ = _sel.select(sockets, [], [], 30)
            except Exception:
                break
            if not r:
                break
            for sock in r:
                try:
                    data = sock.recv(32768)
                except Exception:
                    data = None
                if not data:
                    try: a.close()
                    except: pass
                    try: b.close()
                    except: pass
                    return
                peer = b if sock is a else a
                try:
                    peer.sendall(data)
                except Exception:
                    try: a.close()
                    except: pass
                    try: b.close()
                    except: pass
                    return

    def _handle_client(client_sock):
        """Handle one client connection: CONNECT tunnel or HTTP proxy relay."""
        try:
            client_sock.settimeout(10)
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = client_sock.recv(4096)
                if not chunk:
                    client_sock.close()
                    return
                data += chunk
                if len(data) > 32768:
                    client_sock.close()
                    return

            header_end = data.index(b"\r\n\r\n") + 4
            body_remainder = data[header_end:]
            header_bytes = data[:header_end]
            first_line = header_bytes.split(b"\r\n")[0].decode()
            parts = first_line.split()
            if len(parts) < 2:
                client_sock.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                client_sock.close()
                return

            method = parts[0]

            if method == "CONNECT":
                target = parts[1].split(":")
                target_host = target[0]
                target_port = int(target[1]) if len(target) > 1 else 443
                if protocol == "socks5":
                    upstream_sock = _socks5_connect(target_host, target_port)
                else:
                    upstream_sock = _http_connect(target_host, target_port)
                client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                client_sock.settimeout(None)
                if body_remainder:
                    try: upstream_sock.sendall(body_remainder)
                    except: pass
                _forward_pair(client_sock, upstream_sock)
                return

            # HTTP proxy relay (GET/POST/etc): parse target URL, connect upstream, relay
            target_url = parts[1]
            if "://" not in target_url:
                client_sock.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                client_sock.close()
                return

            from urllib.parse import urlparse as _urlparse
            parsed = _urlparse(target_url)
            target_host = parsed.hostname
            target_port = parsed.port or 80

            if protocol == "socks5":
                upstream_sock = _socks5_connect(target_host, target_port)
            else:
                upstream_sock = _http_connect(target_host, target_port)

            # Rewrite request line to relative path
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            req_line = f"{method} {path} HTTP/1.1\r\n".encode()
            # Keep original headers except Proxy-* headers
            new_headers = []
            for h in header_bytes.split(b"\r\n")[1:]:
                if not h:
                    continue
                if h.lower().startswith(b"proxy-"):
                    continue
                new_headers.append(h)
            new_header_block = req_line + b"\r\n".join(new_headers) + b"\r\n\r\n"
            upstream_sock.sendall(new_header_block)
            if body_remainder:
                try: upstream_sock.sendall(body_remainder)
                except: pass
            client_sock.settimeout(None)
            # Relay response back (upstream -> client, unidirectional for HTTP)
            while True:
                try:
                    chunk = upstream_sock.recv(32768)
                    if not chunk:
                        break
                    client_sock.sendall(chunk)
                except Exception:
                    break
            try: client_sock.close()
            except: pass
            try: upstream_sock.close()
            except: pass
        except Exception as e:
            logger.warning(f"Forward handler error: {e}")
            try: client_sock.close()
            except: pass

    logger.info(f'Starting local proxy localhost:{local_port} -> {protocol}://{host}:{port}')
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", local_port))
        server.listen(32)
        server.settimeout(2.0)
    except Exception as e:
        logger.warning(f"Local proxy bind failed: {e}")
        return None, None

    def _accept_loop():
        while getattr(_accept_loop, "_running", True):
            try:
                client, addr = server.accept()
                t = threading.Thread(target=_handle_client, args=(client,), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception:
                break
        try: server.close()
        except: pass
    _accept_loop._running = True
    t = threading.Thread(target=_accept_loop, daemon=True)
    t.start()

    # Validate local forward chain
    try:
        r = _req.get("http://httpbin.org/ip",
                     proxies={"http": f"http://127.0.0.1:{local_port}"},
                     timeout=timeout)
        ip = r.json().get("origin", "unknown")
        logger.info(f"Proxy chain OK, exit IP: {ip}")
        return local_port, t
    except Exception as e:
        logger.warning(f"Upstream proxy unreachable ({protocol}://{host}:{port}): {e}")
        _accept_loop._running = False
        try: server.close()
        except: pass
        return None, None


def _pick_proxy(strategy, job_index, proxies):
    """从代理列表中按策略选取一个代理. 返回原始字符串或 None."""
    if not proxies: return None
    if strategy == 'sequential':
        idx = (job_index - 1) % len(proxies)
        return proxies[idx]
    else:
        return random.choice(proxies)

# ═══════════════════════════════ CDPBlobCatcher ═══════════════════════════════
class CDPBlobCatcher:
    def __init__(self, debug_port=9222, ws_url=None, label=''):
        self.debug_port = debug_port
        self._ws_url_override = ws_url
        self._label = label
        self.ws = None; self.msg_id = 0
        self.captured_blob = None; self.captured_pk = None
        self.fc_requests = []
        self._lock = threading.Lock()
        self._running = False; self._thread = None
        self._blob_event = threading.Event()
        self._traffic_bytes = 0
        self._requests_log = {}

    def _send(self, method, params=None, session_id=None):
        with self._lock:
            self.msg_id += 1; mid = self.msg_id
            payload = {'id': mid, 'method': method, 'params': params or {}}
            if session_id: payload['sessionId'] = session_id
            try: self.ws.send(json.dumps(payload))
            except Exception: pass
            return mid

    def _get_browser_ws_url(self):
        if self._ws_url_override: return self._ws_url_override
        return _req.get(f'http://localhost:{self.debug_port}/json/version', timeout=5).json()['webSocketDebuggerUrl']

    def start(self):
        ws_url = self._get_browser_ws_url()
        pfx = f'[{self._label}] ' if self._label else ''
        try:
            vi = _req.get(f'http://localhost:{self.debug_port}/json/version', timeout=5).json()
            logger.info(f'{pfx}🌐 Chrome: {vi.get("Browser", "?")}')
        except Exception: pass
        try: self.ws = websocket.create_connection(ws_url, max_size=None, suppress_origin=True)
        except TypeError: self.ws = websocket.create_connection(ws_url, max_size=None, origin='chrome://devtools')
        self._send('Network.enable', {'maxPostDataSize': 131072})
        self._send('Target.setAutoAttach', {'autoAttach': True, 'waitForDebuggerOnStart': True, 'flatten': True})
        self._running = True; self._traffic_bytes = 0
        self._thread = threading.Thread(target=self._loop, daemon=True); self._thread.start()
        logger.info(f'{pfx}🔌 CDP blob 抓取器已启动')

    def _loop(self):
        while self._running:
            try:
                raw = self.ws.recv()
                if not raw: continue
                msg = json.loads(raw)
                method = msg.get('method'); params = msg.get('params', {}); sid = msg.get('sessionId')
                if method == 'Network.requestWillBeSent':
                    req = params.get('request', {}); rid = params.get('requestId'); url = req.get('url', '')
                    if rid: self._requests_log[rid] = {'url': url, 'type': params.get('type', 'Other'), 'method': req.get('method', 'GET'), 'size': 0, 'status': 0}
                    if '/fc/gt2/' in url: self._handle_fc(url, req.get('postData', ''))
                    continue
                if method == 'Network.responseReceived':
                    rid = params.get('requestId'); resp = params.get('response', {})
                    if rid and rid in self._requests_log: self._requests_log[rid]['status'] = resp.get('status', 0)
                    continue
                if method == 'Network.loadingFinished':
                    rid = params.get('requestId'); size = params.get('encodedDataLength', 0)
                    if rid and rid in self._requests_log:
                        self._requests_log[rid]['size'] = size
                        url = self._requests_log[rid].get('url', '')
                        if '127.0.0.1' not in url and 'localhost' not in url: self._traffic_bytes += size
                    continue
                if method == 'Target.attachedToTarget':
                    ns = params.get('sessionId'); waiting = params.get('waitingForDebugger', False)
                    info = params.get('targetInfo', {})
                    self._send('Target.setAutoAttach', {'autoAttach': True, 'waitForDebuggerOnStart': True, 'flatten': True}, session_id=ns)
                    self._send('Fetch.enable', {'patterns': [{'urlPattern': '*/fc/gt2/*', 'requestStage': 'Request'}]}, session_id=ns)
                    self._send('Network.enable', {'maxPostDataSize': 131072}, session_id=ns)
                    if waiting: self._send('Runtime.runIfWaitingForDebugger', {}, session_id=ns)
                    continue
                if method == 'Fetch.requestPaused':
                    req = params.get('request', {}); url = req.get('url', ''); rid = params.get('requestId')
                    if '/fc/gt2/' in url:
                        body = req.get('postData', '')
                        if not body and req.get('hasPostData'):
                            mid = self._send('Fetch.getRequestPostData', {'requestId': rid}, session_id=sid)
                            body = self._wait_result(mid)
                        self._handle_fc(url, body)
                    self._send('Fetch.continueRequest', {'requestId': rid}, session_id=sid)
                    continue
            except Exception:
                if self._running: time.sleep(0.05)

    def _handle_fc(self, url, body):
        if url not in self.fc_requests: self.fc_requests.append(url)
        m = re.search(r'/fc/gt2/public_key/([0-9A-F-]+)', url, re.I)
        if m: self.captured_pk = m.group(1)
        if body:
            bm = re.search(r'data\[blob\]=([^&]+)', body) or re.search(r'(?:^|&)bda=([^&]+)', body)
            if bm:
                new_blob = unquote(bm.group(1))
                if new_blob != self.captured_blob:
                    self.captured_blob = new_blob
                    logger.info(f'📦 CDP 抓到 blob! 长度 {len(self.captured_blob)}, pk={self.captured_pk}')
                self._blob_event.set()

    def _wait_result(self, target_id, timeout=2.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                raw = self.ws.recv(); msg = json.loads(raw)
                if msg.get('id') == target_id: return msg.get('result', {}).get('postData', '')
            except Exception: break
        return ''

    def reset_blob(self):
        self.captured_blob = None; self._blob_event.clear()

    def wait_for_blob(self, timeout=30.0):
        if self._blob_event.wait(timeout): return self.captured_blob
        return None

    def get_traffic_bytes(self): return self._traffic_bytes

    def stop(self):
        self._running = False
        try:
            if self.ws: self.ws.close()
        except Exception: pass

# ═══════════════════════════════ CapMonster Solver ═══════════════════════════════
CAPMONSTER_CREATE_TASK = 'https://api.capmonster.cloud/createTask'
CAPMONSTER_GET_RESULT = 'https://api.capmonster.cloud/getTaskResult'

@dataclass
class CapMonsterSolverConfig:
    api_key: str; poll_interval: float = 2.5; max_wait: float = 120.0; user_agent: Optional[str] = None

class CapMonsterFunCaptchaSolver:
    def __init__(self, config: CapMonsterSolverConfig):
        self.config = config
        self._session = _req.Session(); self._session.headers.update({'Content-Type': 'application/json'})

    def detect(self, driver):
        result = {'found': False, 'siteKey': None, 'surl': None, 'callback': None, 'fcTokenField': None}
        verify_btns = driver.find_elements(By.XPATH, '//div[@id="root"]//button')
        for btn in verify_btns:
            try:
                txt = (btn.text or '').strip()
                if '验证' in txt or 'Verify' in txt.lower(): result['found'] = True; break
            except Exception: pass
        caps = driver.find_elements(By.ID, 'capture-arkose')
        if caps:
            result['found'] = True; result['fcTokenField'] = '#capture-arkose'
            dsrc = caps[0].get_attribute('data-arkose-src') or ''
            m = re.search(r'/v\d+/([0-9A-F-]+)/api\.js', dsrc, re.I)
            if m: result['siteKey'] = m.group(1)
            sm = re.search(r'//([a-zA-Z0-9_.-]*arkoselabs\.com)', dsrc, re.I)
            if sm: result['surl'] = sm.group(1)
        if not result['found']:
            iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe[src*=".arkoselabs.com"], iframe[src*="funcaptcha.com"]')
            if iframes:
                result['found'] = True; src = iframes[0].get_attribute('src') or ''
                if not result['siteKey']:
                    m = re.search(r'#([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})', src, re.I)
                    if m: result['siteKey'] = m.group(1)
                if not result['surl']:
                    sm = re.search(r'//([a-zA-Z0-9_.-]*arkoselabs\.com)', src, re.I)
                    if sm: result['surl'] = sm.group(1)
        if not result['found'] or not result['siteKey']:
            gcf = driver.find_elements(By.CSS_SELECTOR, 'iframe#game-core-frame, iframe[title="视觉挑战"]')
            if gcf:
                result['found'] = True; src = gcf[0].get_attribute('src') or ''
                if not result['siteKey']:
                    m = re.search(r'[?&]pk=([0-9A-F-]+)', src, re.I)
                    if m: result['siteKey'] = m.group(1)
                if not result['surl']:
                    sm = re.search(r'//([a-zA-Z0-9_.-]*arkoselabs\.com)', src, re.I)
                    if sm: result['surl'] = sm.group(1)
        return result

    def _create_task(self, website_url, website_public_key, data_blob=None, surl=None, user_agent=None):
        task = {'type': 'FunCaptchaTask', 'websiteURL': website_url, 'websitePublicKey': website_public_key}
        if data_blob: task['data'] = json.dumps({'blob': data_blob})
        if surl and surl != 'client-api.arkoselabs.com': task['funcaptchaApiJSSubdomain'] = surl
        final_ua = user_agent or self.config.user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
        task['userAgent'] = final_ua
        try:
            r = self._session.post(CAPMONSTER_CREATE_TASK, json={'clientKey': self.config.api_key, 'task': task}, timeout=15)
            data = r.json(); task_id = data.get('taskId')
            if not task_id: logger.error(f'createTask 失败: {str(data)[:200]}'); return None
            logger.info(f'📡 CapMonster taskId={task_id}'); return task_id
        except Exception as e: logger.error(f'createTask 异常: {e}'); return None

    def _poll_task(self, task_id):
        deadline = time.time() + self.config.max_wait; pc = 0
        while time.time() < deadline:
            pc += 1
            try:
                r = self._session.post(CAPMONSTER_GET_RESULT, json={'clientKey': self.config.api_key, 'taskId': task_id}, timeout=10)
                data = r.json()
            except Exception as e: logger.warning(f'轮询异常: {e}'); time.sleep(self.config.poll_interval); continue
            status = data.get('status')
            logger.info(f'🔄 轮询 #{pc}: status={status}')
            if status == 'ready':
                token = data.get('solution', {}).get('token')
                if token: logger.info(f'✅ 求解成功 (token 长度 {len(token)})'); return token
                return None
            eid = data.get('errorId')
            if (eid not in (None, 0)) or status in ('error', 'failed'): logger.error(f'❌ 求解失败: {str(data)[:200]}'); return None
            time.sleep(self.config.poll_interval)
        logger.error(f'⏱️ 轮询超时 ({pc} 次)'); return None

    def solve(self, driver, blob=None):
        info = self.detect(driver)
        if not info.get('found'): logger.warning('未检测到 FunCaptcha'); return None
        site_key = info.get('siteKey')
        if not site_key: logger.error('未找到 siteKey'); return None
        website_url = driver.current_url
        user_agent = self.config.user_agent
        if not user_agent:
            try: user_agent = driver.execute_script('return navigator.userAgent;')
            except Exception: pass
        logger.info(f'📋 siteKey={site_key}, surl={info.get("surl")}, blob={"有("+str(len(blob))+")" if blob else "无"}')
        task_id = self._create_task(website_url=website_url, website_public_key=site_key, data_blob=blob, surl=info.get('surl'), user_agent=user_agent)
        if not task_id: return None
        return self._poll_task(task_id)

    # ═══ 修复点1: 关隐式等待 ═══
    def _suspend_iw(self, driver):
        prev = IMPLICIT_WAIT_SEC
        try: driver.implicitly_wait(0)
        except Exception: pass
        return lambda: driver.implicitly_wait(prev)

    def _click_arkose_verify_button(self, driver, max_depth=3):
        restore = self._suspend_iw(driver)
        try:
            def try_click():
                for sel in ['button[data-theme="home.verifyButton"]', 'button[aria-label="验证"]', 'button[aria-label="Verify"]']:
                    try:
                        for btn in driver.find_elements(By.CSS_SELECTOR, sel):
                            try:
                                if btn.is_displayed():
                                    driver.execute_script('arguments[0].click();', btn)
                                    return True
                            except Exception: pass
                    except Exception: pass
                return False
            def recurse(depth):
                if try_click(): return True
                if depth >= max_depth: return False
                try: iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                except Exception: iframes = []
                for ifr in iframes:
                    try: driver.switch_to.frame(ifr)
                    except Exception: continue
                    try:
                        if recurse(depth + 1): return True
                    finally:
                        try: driver.switch_to.parent_frame()
                        except Exception: driver.switch_to.default_content()
                return False
            driver.switch_to.default_content()
            found = recurse(0)
            driver.switch_to.default_content()
            if found: logger.info('🖱️ 已点击 Arkose 验证按钮')
            return found
        finally:
            restore()

    def inject_token(self, driver, token):
        try:
            result = driver.execute_script('''
                var token = arguments[0];
                var form = document.querySelector('form#flow-form') || document.querySelector('form[action*="captcha-gate"]');
                if (!form) return {ok:false, reason:'no-form'};
                var arkose = form.querySelector('input[name="arkose"]') || document.querySelector('#capture-arkose');
                if (!arkose) return {ok:false, reason:'no-arkose-input'};
                var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(arkose, token);
                arkose.dispatchEvent(new Event('input', {bubbles:true}));
                arkose.dispatchEvent(new Event('change', {bubbles:true}));
                try {
                    if (typeof form.requestSubmit === 'function') form.requestSubmit();
                    else form.submit();
                    return {ok:true, method:'requestSubmit', arkoseSet: arkose.value === token};
                } catch(e) { return {ok:false, reason:'submit-error:'+e.message}; }
            ''', token)
            if result and result.get('ok'): logger.info(f'💉 token 注入成功: {result.get("method")}'); return True
            logger.warning(f'注入失败: {result}')
        except Exception as e: logger.warning(f'注入异常: {e}')
        return False

    # ═══ 修复点2: blob 不丢，新抓不到用旧的 ═══
    def solve_and_inject(self, driver, timeout=90.0, blob_catcher=None):
        deadline = time.time() + timeout; detected = False; pc = 0
        while time.time() < deadline:
            pc += 1
            try:
                result = self.detect(driver)
                if pc % 10 == 0: logger.info(f'🔄 已探测 {pc} 次, found={result.get("found")}')
                if result.get('found'): detected = True; logger.info(f'🎯 FunCaptcha 已检测到 (siteKey={result.get("siteKey")})'); break
            except Exception as e: logger.warning(f'探测异常: {e}')
            time.sleep(0.5)
        if not detected: logger.warning('⏱️ 等待 FunCaptcha 超时 (正常)'); return True

        # ⚡ 修复: 先记下旧 blob，reset 只是清 event
        blob_before = blob_catcher.captured_blob if blob_catcher else None
        if blob_catcher: blob_catcher.reset_blob()

        def _try_click(t=30.0):
            dl = time.time() + t
            while time.time() < dl:
                if self._click_arkose_verify_button(driver): return True
                time.sleep(2.0)
            return False

        if not _try_click():
            logger.warning('⚠️ 30s 未点到验证按钮, 刷新重试')
            driver.refresh(); time.sleep(5)
            if blob_catcher: blob_catcher.reset_blob(); blob_before = None
            _try_click()

        # 等新 blob，15s 超时 (缩短)，没等到就用旧的
        blob_new = None
        if blob_catcher is not None:
            logger.info('⏳ 等待 CDP 抓取 blob (点击后)...')
            blob_new = blob_catcher.wait_for_blob(timeout=15.0)
            if blob_new: logger.info(f'📦 CDP 抓到点击后 blob (长度 {len(blob_new)})')

        blob = blob_new or blob_before
        if blob:
            logger.info(f'📦 使用 blob (长度 {len(blob)}, 来源: {"点击后" if blob_new else "点击前"})')
        else:
            logger.warning('⚠️ 无 blob (点击前后都没抓到)')

        token = self.solve(driver, blob=blob)
        if not token: return False
        ok = self.inject_token(driver, token)

        # 检测结果
        dl2 = time.time() + 15.0
        while time.time() < dl2:
            try:
                state = driver.execute_script('''
                    if (document.querySelector('#success-icon > svg > path')) return 'success';
                    var err = document.querySelector('[class*="error"], [role="alert"]');
                    if (err && /无效|invalid|失败/i.test(err.textContent || '')) return 'rejected';
                    return null;
                ''')
                if state == 'success': logger.info('✅ 验证通过!'); return True
                if state == 'rejected': logger.warning('⚠️ token 被拒'); return False
            except Exception: pass
            time.sleep(0.4)
        logger.info('ℹ️ 15s 未见结果页, 交由后续判定')
        return ok

# ═══════════════════════════════ 浏览器 ═══════════════════════════════
def create_driver(proxy_local_port=None):
    options = Options()
    for arg in ['--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu',
                '--window-size=1920,1080','--incognito',
                f'--remote-debugging-port={CDP_DEBUG_PORT}','--remote-allow-origins=*',
                '--disable-blink-features=AutomationControlled',
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36']:
        options.add_argument(arg)
    options.add_argument('--lang=en-GB')
    options.add_argument('--accept-lang=en-GB,en')
    if proxy_local_port:
        options.add_argument(f'--proxy-server=http://127.0.0.1:{proxy_local_port}')
        logger.info(f'🔒 Chrome 代理 → localhost:{proxy_local_port}')
    else:
        logger.info('🌐 Chrome 直连模式')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # Inject anti-fingerprinting script before any page JavaScript runs
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': STEALTH_JS})
    driver.implicitly_wait(IMPLICIT_WAIT_SEC)
    return driver

# ═══════════════════════════════ 注册流程 (batch_register.py 风格) ═══════════════════════════════
def register_one(acc, proxy_local_port=None):
    driver = create_driver(proxy_local_port)
    solver = None
    if CAPMONSTER_API_KEY:
        solver = CapMonsterFunCaptchaSolver(CapMonsterSolverConfig(api_key=CAPMONSTER_API_KEY, max_wait=300.0))
        logger.info('🛡️ CapMonster 求解器已就绪')

    blob_catcher = None
    try:
        def _wait_or_refresh(selector, desc, timeout=25):
            try:
                is_error = driver.execute_script(
                    "return document.querySelector('#main-frame-error') !== null"
                    " || document.body?.classList?.contains('neterror')"
                    " || document.title.includes('无法访问')")
            except Exception: is_error = False
            if is_error:
                logger.warning(f'⚠️ 检测到错误页 ({desc}), 立即刷新...')
                driver.execute_script('location.reload(true);'); time.sleep(3)
            try:
                return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            except TimeoutException:
                logger.warning(f'⚠️ {desc} 超时 (等{timeout}s), 硬刷新...')
                driver.execute_script('location.reload(true);'); time.sleep(5)
                el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f'🔄 刷新后 {desc} 已出现'); return el

        # ── 打开页面 ──
        logger.info(f'📄 打开: {REGISTER_URL}')
        driver.get(REGISTER_URL)

        try:
            driver.implicitly_wait(0)
            WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button#onetrust-reject-all-handler, button.ot-reject-all, button[id*="reject"]'))).click()
            logger.info('🍪 已关闭 Cookie 横幅')
        except TimeoutException: pass
        finally: driver.implicitly_wait(IMPLICIT_WAIT_SEC)

        # ── 步骤1: 邮箱 ──
        logger.info(f'📧 {acc["email"]}')
        driver.find_element(By.ID, 'accountName').send_keys(acc['email'])
        time.sleep(0.5); driver.find_element(By.XPATH, "//*[@id='submit']").click(); time.sleep(2)

        # ── 步骤2: 国家 (先 reload!) ──
        _wait_or_refresh('#capture-country', '国家选择器')
        logger.info('🔄 刷新页面确保完整加载...')
        driver.execute_script('location.reload(true);'); time.sleep(3)
        _wait_or_refresh('#capture-country', '国家选择器(刷新后)')
        logger.info(f'🌍 国家: {COUNTRY}')
        Select(driver.find_element(By.ID, 'capture-country')).select_by_value(COUNTRY); time.sleep(1.5)

        # ── 步骤3: 生日 (JS setter) ──
        try:
            driver.implicitly_wait(0)
            cb = driver.find_element(By.CSS_SELECTOR, 'button#onetrust-reject-all-handler, button[id*="reject"]')
            if cb.is_displayed(): cb.click(); logger.info('🍪 关闭晚出现的 Cookie'); time.sleep(0.5)
        except Exception: pass
        finally: driver.implicitly_wait(IMPLICIT_WAIT_SEC)

        logger.info(f'🎂 {acc["birth_year"]}-{acc["birth_month"]}-{acc["birth_day"]}')
        driver.find_element(By.NAME, 'dob-plain').click(); time.sleep(0.8)
        driver.execute_script('''
            var year=arguments[0], month=arguments[1], day=arguments[2];
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            var c = document.querySelector('#dob-field-active'); if (!c) return;
            c.querySelectorAll('input').forEach(function(inp){
                var cls = inp.className || '';
                if (cls.indexOf('--yyyy')!==-1) setter.call(inp, year);
                else if (cls.indexOf('--mm')!==-1) setter.call(inp, month);
                else if (cls.indexOf('--dd')!==-1) setter.call(inp, day);
                inp.dispatchEvent(new Event('input', {bubbles:true}));
                inp.dispatchEvent(new Event('change', {bubbles:true}));
            });
        ''', acc['birth_year'], acc['birth_month'], acc['birth_day'])
        time.sleep(0.5); driver.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').click(); time.sleep(2)

        # ── 步骤4: 姓名 (带重试) ──
        logger.info(f'👤 {acc["first_name"]} {acc["last_name"]}')
        try:
            fi = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#capture-first-name')))
            fi.click(); time.sleep(0.2); fi.send_keys(acc['first_name']); time.sleep(0.3)
            driver.find_element(By.CSS_SELECTOR, '#capture-last-name').send_keys(acc['last_name']); time.sleep(0.3)
        except TimeoutException:
            logger.warning('⚠️ 姓名框未出现, 刷新重试')
            driver.refresh(); time.sleep(5)
            fi = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#capture-first-name')))
            fi.click(); time.sleep(0.2); fi.send_keys(acc['first_name']); time.sleep(0.3)
            driver.find_element(By.CSS_SELECTOR, '#capture-last-name').send_keys(acc['last_name']); time.sleep(0.3)
            logger.info('🔄 刷新后姓名填写成功')
        driver.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').click(); time.sleep(2)

        # ── 步骤5: 邮箱确认 ──
        actual_email = driver.find_element(By.CSS_SELECTOR, '#capture-email').get_attribute('value')
        if actual_email == acc['email']:
            logger.info(f'✅ 邮箱一致: {actual_email}')
            driver.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').click(); time.sleep(2)
        else:
            logger.error(f'❌ 邮箱不一致! {actual_email}'); driver.save_screenshot('error_email.png'); return False

        # ── 步骤6: 协议 (JS checked setter) ──
        logger.info('📋 勾选协议'); time.sleep(1)
        driver.execute_script('''
            ['#capture-opt-in-blizzard-news-special-offers','#legal-checkboxes > label > input.step__checkbox'].forEach(function(sel){
                var el = document.querySelector(sel);
                if (el && !el.checked) {
                    var s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked').set;
                    s.call(el, true);
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                }
            });
        ''')
        time.sleep(0.5); driver.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').click(); time.sleep(2)

        # ── 步骤7: 密码 ──
        logger.info(f'🔑 密码: {acc["password"]}')
        _wait_or_refresh('#capture-password', '密码输入框')
        driver.find_element(By.CSS_SELECTOR, '#capture-password').send_keys(acc['password'])
        time.sleep(0.5); driver.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').click(); time.sleep(2)

        # ── 步骤8: BattleTag + CDP + FunCaptcha ──
        logger.info(f'🏷️ {acc["battle_tag"]}')
        _wait_or_refresh('#capture-battletag', 'BattleTag输入框')
        bt = driver.find_element(By.CSS_SELECTOR, '#capture-battletag')
        driver.execute_script(
            'var el=arguments[0];'
            'var s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set;'
            's.call(el,arguments[1]);'
            'el.dispatchEvent(new Event("input",{bubbles:true}));'
            'el.dispatchEvent(new Event("change",{bubbles:true}));',
            bt, acc['battle_tag'])
        time.sleep(0.5)

        try:
            WebDriverWait(driver, 5).until(lambda d: not d.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').get_attribute('disabled'))
        except TimeoutException: logger.warning('⚠️ submit-btn 启用等待超时')

        # ⚠️ CDP 只在 BattleTag 提交前启动
        if solver:
            try: blob_catcher = CDPBlobCatcher(debug_port=CDP_DEBUG_PORT, label='1'); blob_catcher.start()
            except Exception as e: logger.warning(f'⚠️ CDP 启动失败: {e}'); blob_catcher = None

        logger.info('➡️ 提交 BattleTag')
        driver.find_element(By.CSS_SELECTOR, '#flow-form-submit-btn').click(); time.sleep(2)

        if solver:
            logger.info('⏳ 等待 FunCaptcha 弹窗出现...')
            try: ok = solver.solve_and_inject(driver, timeout=90.0, blob_catcher=blob_catcher)
            finally:
                if blob_catcher: blob_catcher.stop()
            if not ok: logger.error('❌ FunCaptcha 求解失败'); driver.save_screenshot('error_captcha.png'); return False

        # ── 步骤9: 成功页 ──
        logger.info('⏳ 等待注册成功...')
        try:
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#success-icon > svg > path')))
            logger.info('✅ 注册成功!')
            with open('registered_account.txt', 'a', encoding='utf-8') as f:
                f.write(f'账号：{acc["email"]}\n密码：{acc["password"]}\n\n')
            logger.info(f'💾 已保存: {acc["email"]}'); driver.save_screenshot('success.png'); return True
        except TimeoutException:
            logger.error(f'❌ 等待成功超时, URL={driver.current_url[:100]}')
            driver.save_screenshot('error_timeout.png'); return False

    except Exception as e:
        logger.error(f'❌ 异常: {type(e).__name__}: {e}', exc_info=True)
        try: driver.save_screenshot('error_exception.png')
        except Exception: pass
        return False
    finally:
        if blob_catcher:
            try: blob_catcher.stop()
            except Exception: pass
        driver.quit()


def main():
    proxies_raw = os.environ.get('PROXIES_JSON', '[]')
    try: all_proxies = json.loads(proxies_raw)
    except (json.JSONDecodeError, TypeError): all_proxies = []
    strategy = os.environ.get('PROXY_STRATEGY', 'random')
    job_index = int(os.environ.get('MATRIX_INDEX', '1'))

    proxy_local_port = None
    proxy_proc = None
    if all_proxies:
        raw = _pick_proxy(strategy, job_index, all_proxies)
        if raw:
            parsed = _parse_proxy_line(raw)
            if parsed:
                logger.info(f'🎯 选中代理 [{strategy}]: {parsed[1]}:{parsed[2]}')
                proxy_local_port, proxy_proc = _start_local_proxy(parsed)
                if not proxy_local_port:
                    logger.warning('⚠️ 代理启动失败，回退直连')
            else:
                logger.warning(f'⚠️ 代理解析失败，回退直连: {raw}')
    else:
        logger.info('📋 未配置代理，直连模式')

    acc = generate_identity()
    logger.info('=' * 50)
    logger.info('🚀 战网自动注册 — CI v2 批量并行')
    logger.info(f'   Job #{os.environ.get("MATRIX_INDEX", "?")}')
    logger.info(f'   邮箱: {acc["email"]}')
    logger.info(f'   BattleTag: {acc["battle_tag"]}')
    if proxy_local_port:
        logger.info(f'   代理: localhost:{proxy_local_port}')
    logger.info('=' * 50)

    try:
        ok = register_one(acc, proxy_local_port)
    finally:
        if proxy_proc:
            if hasattr(proxy_proc, 'poll'):
                if proxy_proc.poll() is None:
                    proxy_proc.kill()
            # else: daemon thread, dies with process
            logger.info('🛑 代理进程已清理')
    logger.info(f'\n🏁 注册结束: {"✅ 成功" if ok else "❌ 失败"}')


if __name__ == '__main__':
    main()

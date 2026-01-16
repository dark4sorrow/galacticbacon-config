from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import threading
import time
import subprocess
import shutil
import socket
import psutil
import urllib.request
import xml.etree.ElementTree as ET
import ssl
import nmap
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'SUPER_SECRET_KEY_CHANGE_THIS_LOCALLY' # Session security key

# --- AUTHENTICATION SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Hardcoded User Database
USERS = {
    "admin": {"password": "netsys"} 
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

# --- HTML & AUTH ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username]['password'] == password:
            login_user(User(username))
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/ups_dashboard.html')
@login_required
def ups_dashboard():
    return render_template('ups_dashboard.html')

@app.route('/nmap_index.html')
@login_required
def nmap_dashboard():
    return render_template('nmap_index.html')

@app.route('/ssl_dashboard.html')
@login_required
def ssl_dashboard():
    return render_template('ssl_dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- CONFIGURATION ---
PORT = 5001
COMMUNITY_STRING = 's1lentb0b'
POLL_INTERVAL_UPS = 30
POLL_INTERVAL_DOMAINS = 3600

SSL_DOMAINS = [
    "ADFS.nic.edu", "IDM1.nic.edu", "IDM2.nic.edu", "IVCVideo.nic.edu", "RDG2.nic.edu",
    "TIDM.nic.edu", "av.nic.edu", "aviso.nic.edu", "bomgar.nic.edu", "boulder.nic.edu",
    "br1.nic.edu", "campusrec.nic.edu", "campusweb.nic.edu", "clconnect.nic.edu",
    "collui.nic.edu", "coursecontent.nic.edu", "dropbox.nic.edu", "elk8-prod.nic.edu",
    "elk9-test.nic.edu", "etcentral.nic.edu", "etsts.nic.edu", "expressway-edge.nic.edu",
    "ezproxy1.nic.edu", "ftpsec.nic.edu", "fusion.nic.edu", "gve.nic.edu", "hostheader.nic.edu",
    "icanhasvpn.nic.edu", "idm.nic.edu", "idmp.nic.edu", "idp.nic.edu", "infoblox.nic.edu",
    "ivc.nic.edu", "learningspace.nic.edu", "login.ezproxy1.nic.edu", "mail2019.nic.edu",
    "mailr1.nic.edu", "mailr2.nic.edu", "mdc-vpngw-1.nic.edu", "mobis.nic.edu",
    "mynic.nic.edu", "mynic13.nic.edu", "nic.edu", "nicdc1.nic.edu", "nicdc5.nic.edu",
    "nicns1.nic.edu", "nicns2.nic.edu", "niconline.nic.edu", "nicstream.nic.edu",
    "nps-nac1.nic.edu", "nps-nac2.nic.edu", "nps.nic.edu", "ns1.cite.nic.edu",
    "ns2.cite.nic.edu", "olap.nic.edu", "pbi.nic.edu", "pcomm.nic.edu", "prv.nic.edu",
    "rdg.nic.edu", "sdc-t2019-dcc02.nic.edu", "sdc-vpngw-1.nic.edu", "sftp.nic.edu",
    "stars.nic.edu", "tclconnect.nic.edu", "tcollui.nic.edu", "tcss.nic.edu",
    "testcomm.nic.edu", "testetcentral.nic.edu", "testmynic.nic.edu", "touchnet.nic.edu",
    "tprv.nic.edu", "ttouchnet.nic.edu", "twebsvc.nic.edu", "twebsvc2.nic.edu",
    "twebsvcfe.nic.edu", "vcse.nic.edu", "video.nic.edu", "vidtest.nic.edu",
    "vpn.nic.edu", "vpn2.nic.edu", "web.nic.edu", "webapps.nic.edu", "webcon.nic.edu",
    "websvc.nic.edu", "websvc2.nic.edu", "websvcfe.nic.edu", "ww2.nic.edu"
]

UPS_NAME_MAPPING = {
    "10.1.9.224": "Boswell MDF", "10.1.9.239": "Children's Center MDF", "10.1.9.248": "DARM MDF",
    "10.1.9.249": "DARM IDF", "10.1.9.212": "FSOQ MDF", "10.1.9.250": "FSOQ2 MDF", "10.1.9.233": "GYM MDF",
    "10.1.9.234": "GYM IDF B", "10.1.9.215": "Hedlund MDF", "10.1.9.242": "Hedlund IDF B", "10.1.9.221": "HSB MDF",
    "10.1.9.222": "HSB IDF", "10.1.9.228": "HSB IDF2", "10.1.9.213": "IAB MDF", "10.1.9.227": "HWC A MDF",
    "10.1.9.245": "HWC HR", "10.1.9.244": "HWC-C Maint", "10.1.9.217": "HWC Security", "10.1.9.237": "HWC E",
    "10.1.9.218": "Kildow MDF", "10.1.9.238": "Kildow IDF", "10.1.9.209": "Lee Hall 212", "10.1.9.208": "Lee Hall MDF",
    "10.1.9.240": "McLain Hall MDF", "10.1.9.214": "Molstead MDF", "10.1.9.241": "Molstead IDF B",
    "10.1.9.243": "Molstead IDF D", "10.1.9.211": "Post Hall MDF", "10.1.9.246": "Residence Hall",
    "10.3.9.213": "Sandpoint ANX", "10.1.9.230": "Seiter MDF", "10.1.9.231": "Seiter IDF B",
    "10.1.9.232": "Seiter IDF C", "10.1.9.223": "Sherman MDF", "10.1.9.254": "Siebert MDF",
    "10.1.9.253": "Siebert IDF", "10.1.9.220": "SUB MDF", "10.1.9.219": "SUB IDF B", "10.1.9.210": "SUB IDF C",
    "10.1.9.216": "SUB IDF D", "10.1.9.247": "Wellness Center MDF", "10.1.9.226": "Winton MDF",
    "10.102.0.100": "AAoA", "10.9.9.42": "CTE MDF", "10.9.9.43": "CTE IDF A", "10.9.9.44": "CTE IDF B",
    "10.101.0.200": "Head Start", "10.8.1.9": "POST ACADEMY MDF", "10.3.9.212": "Sandpoint IDF",
    "10.2.9.13": "WFT MDF2"
}

OID_ORDER = [
    "1.3.6.1.4.1.318.1.1.1.1.1.1.0", "1.3.6.1.4.1.318.1.1.1.4.1.1.0", "1.3.6.1.4.1.318.1.1.1.2.2.1.0",
    "1.3.6.1.4.1.318.1.1.1.3.2.1.0", "1.3.6.1.4.1.318.1.1.1.4.2.1.0", "1.3.6.1.4.1.318.1.1.1.4.2.3.0",
    "1.3.6.1.4.1.318.1.1.1.7.2.3.0", "1.3.6.1.4.1.318.1.1.1.2.2.3.0", "1.3.6.1.4.1.318.1.1.1.2.1.1.0"
]

DETAILED_STATUS_MAP = {
    4: "Smart Boost", 5: "Smart Trim", 6: "Software Bypass",
    7: "Output Off", 8: "Rebooting", 9: "Switched Bypass", 10: "Hardware Failure"
}

ups_data_cache = {}
protocol_cache = {}
domain_audit_cache = []

# --- HELPERS ---
def detect_protocol(ip):
    if ip in protocol_cache: return protocol_cache[ip]
    try:
        with socket.create_connection((ip, 443), timeout=0.5):
            protocol_cache[ip] = "https"
            return "https"
    except:
        protocol_cache[ip] = "http"
        return "http"

def analyze_headers(domain):
    issues = []
    headers_summary = {"hsts": False, "xframe": False, "server_leak": False}
    try:
        url = f"https://{domain}"
        req = urllib.request.Request(url, method="HEAD", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            headers = response.headers
            if 'Strict-Transport-Security' in headers: headers_summary['hsts'] = True
            else: issues.append("Missing HSTS")
            if 'X-Frame-Options' in headers: headers_summary['xframe'] = True
            else: issues.append("Missing X-Frame-Options")
            srv = headers.get('Server', '')
            if any(char.isdigit() for char in srv):
                headers_summary['server_leak'] = True
                issues.append(f"Server Leak: {srv}")
    except Exception:
        issues.append("Header Scan Failed")
    return headers_summary, issues

def audit_single_domain(domain):
    result = {"domain": domain, "days_remaining": -1, "expiry_date": "Unknown", "ssl_status": "Error", "issues": [], "grade": "F"}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                not_after = cert['notAfter']
                expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_remaining = (expiry_date - datetime.utcnow()).days
                result["expiry_date"] = expiry_date.strftime("%Y-%m-%d")
                result["days_remaining"] = days_remaining
                if days_remaining < 7: result["ssl_status"] = "Critical"
                elif days_remaining < 30: result["ssl_status"] = "Warning"
                else: result["ssl_status"] = "Good"
        headers, header_issues = analyze_headers(domain)
        result["issues"] = header_issues
        if result["ssl_status"] != "Good": result["grade"] = "F"
        elif not headers['hsts']: result["grade"] = "C"
        elif headers['server_leak']: result["grade"] = "B"
        else: result["grade"] = "A"
    except Exception as e:
        result["expiry_date"] = "Conn Error"
        result["grade"] = "X"
    return result

def poll_ups_devices():
    while True:
        threads = []
        for ip, name in UPS_NAME_MAPPING.items():
            t = threading.Thread(target=lambda i=ip, n=name: ups_data_cache.update({i: get_snmp_data(i, n)}))
            threads.append(t)
            t.start()
        for t in threads: t.join()
        time.sleep(POLL_INTERVAL_UPS)

def poll_domains():
    global domain_audit_cache
    while True:
        results = []
        for domain in SSL_DOMAINS:
            results.append(audit_single_domain(domain))
        results.sort(key=lambda x: (x['grade'], x['days_remaining']))
        domain_audit_cache = results
        time.sleep(POLL_INTERVAL_DOMAINS)

def get_snmp_data(ip, name):
    res = {"ipAddress": ip, "name": name, "status": "Offline", "model": "N/A", "batteryCapacity": "0", "inputVoltage": "0", "outputVoltage": "0", "load": "0", "lastTestDate": "N/A", "runtime": "N/A", "batteryDate": "N/A", "statusClass": "status-offline", "protocol": "http"}
    try:
        res["protocol"] = detect_protocol(ip)
        cmd = ["snmpget", "-v1", "-c", COMMUNITY_STRING, "-Oqv", ip] + OID_ORDER
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=2.5)
        if proc.returncode != 0: return res
        lines = proc.stdout.strip().split('\n')
        if len(lines) < 9: return res
        
        raw_status = int(lines[1])
        if raw_status in [1, 2]: res.update({"status": "Online", "statusClass": "status-online"})
        elif raw_status == 3: res.update({"status": "On Battery", "statusClass": "status-on-battery"})
        elif raw_status in DETAILED_STATUS_MAP: res.update({"status": DETAILED_STATUS_MAP[raw_status], "statusClass": "status-needs-attention"})
        else: res.update({"status": f"Code {raw_status}", "statusClass": "status-needs-attention"})

        res.update({
            "model": lines[0].strip('"'), "batteryCapacity": lines[2].strip('"'),
            "inputVoltage": lines[3].strip('"'), "outputVoltage": lines[4].strip('"'),
            "load": lines[5].strip('"'), "lastTestDate": lines[6].strip('"'),
            "runtime": lines[7].strip('"'), "batteryDate": lines[8].strip('"')
        })
        return res
    except: return res

# --- API ENDPOINTS ---

@app.route('/api/ups-status', methods=['GET'])
@login_required
def get_status(): return jsonify(list(ups_data_cache.values()))

@app.route('/api/server-stats', methods=['GET'])
@login_required
def get_server_stats():
    # 1. CPU & Load
    cpu_pct = psutil.cpu_percent(interval=None)
    load1, load5, load15 = psutil.getloadavg()
    
    # 2. RAM & Swap
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # 3. Disk
    disk = psutil.disk_usage('/')
    
    # 4. Uptime Calculation
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime_delta = datetime.now() - boot_time
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m"

    # 5. IP Address
    try:
        # Trick to find primary IP without connecting to internet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "127.0.0.1"

    return jsonify({
        "cpu": cpu_pct,
        "load_1": round(load1, 2),
        "load_5": round(load5, 2),
        "ram_percent": ram.percent,
        "swap_percent": swap.percent,
        "disk_percent": disk.percent,
        "uptime": uptime_str,
        "ip": ip
    })

@app.route('/api/cisa-feed', methods=['GET'])
@login_required
def get_cisa_feed():
    # UPDATED URL TO THE WORKING FEED
    feed_url = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
    items = []
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=10) as response:
            root = ET.fromstring(response.read())
            # Standard RSS parsing
            for item in root.findall('./channel/item')[:6]: 
                items.append({"title": item.find('title').text, "link": item.find('link').text, "pubDate": item.find('pubDate').text})
    except Exception as e:
        print(f"CISA Feed Error: {e}")
        return jsonify([]), 200 
    return jsonify(items)

@app.route('/api/domain-audit', methods=['GET'])
@login_required
def get_domain_audit():
    return jsonify(domain_audit_cache)

@app.route('/api/nmap-scan', methods=['GET'])
@login_required
def run_nmap_scan():
    target = request.args.get('target')
    scan_type = request.args.get('type', 'quick')
    if not target: return jsonify({"error": "No target specified"}), 400
    nm = nmap.PortScanner()
    try:
        if scan_type == 'quick': args = '-T4 -F' 
        elif scan_type == 'intense': args = '-T4 -A -v'
        elif scan_type == 'vuln': args = '-T4 --script=vuln'
        else: args = '-T4 -F'
        nm.scan(target, arguments=args)
        if target in nm.all_hosts():
            host_data = nm[target]
            open_ports = []
            for proto in host_data.all_protocols():
                ports = host_data[proto].keys()
                for port in sorted(ports):
                    if host_data[proto][port]['state'] == 'open':
                        svc = host_data[proto][port]
                        open_ports.append({"port": port, "protocol": proto, "service": svc['name'], "detail": f"{svc.get('product','')} {svc.get('version','')}".strip()})
            return jsonify({"status": "up", "hostname": host_data.hostname(), "ports": open_ports, "command": nm.command_line()})
        else: return jsonify({"status": "down", "message": "Host unreachable"})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not shutil.which("snmpget"): exit(1)
    threading.Thread(target=poll_ups_devices, daemon=True).start()
    threading.Thread(target=poll_domains, daemon=True).start()
    app.run(host='127.0.0.1', port=PORT, debug=False)

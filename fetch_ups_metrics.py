import json
import os
import subprocess
import sys

# Explicit path for damurphy on GalacticBacon
UPS_PROJECT_PATH = "/home/damurphy/ups_project"
INVENTORY_FILE = os.path.join(UPS_PROJECT_PATH, "ups_inventory.json")

# Verified OIDs from ups_server.py
OID_LOAD = "1.3.6.1.4.1.318.1.1.1.4.2.1.0"
OID_CAPACITY = "1.3.6.1.4.1.318.1.1.1.2.2.1.0"

def snmp_get(ip, oid):
    """Simple wrapper for snmpget command line using s1lentb0b."""
    try:
        # Using -v1 and s1lentb0b as defined in ups_server.py
        cmd = ["snmpget", "-v1", "-c", "s1lentb0b", "-Oqv", ip, oid]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=2).decode().strip()
        
        # Clean non-numeric characters
        clean_val = ''.join(filter(str.isdigit, output))
        if not clean_val:
            return None
            
        val = int(clean_val)
        
        # Logic to handle potential 10x scaling in SNMP returns
        if oid == OID_LOAD and val > 100:
            return val / 10.0
        return float(val)
    except:
        return None

def ping_check(ip):
    """Returns True if host responds to ping."""
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "1", ip], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False

def get_ups_status():
    if not os.path.exists(INVENTORY_FILE):
        return f"Error: {INVENTORY_FILE} not found."

    try:
        with open(INVENTORY_FILE, 'r') as f:
            inventory = json.load(f)
        
        total_units = len(inventory)
        online_units = 0
        offline_units = 0
        total_load_pct = 0
        total_capacity_pct = 0
        data_points = 0
        current_count = 0

        print(f"Starting Scan of {total_units} UPS units on nic.edu network...")

        for ip, location in inventory.items():
            current_count += 1
            sys.stdout.write(f"\r[SCANNING {current_count}/{total_units}] Checking: {ip} ({location[:20]}...)   ")
            sys.stdout.flush()

            if ping_check(ip):
                online_units += 1
                load = snmp_get(ip, OID_LOAD)
                cap = snmp_get(ip, OID_CAPACITY)
                
                if load is not None and cap is not None:
                    # Sanity check: cap load at 100% for averages unless truly overloaded
                    total_load_pct += min(load, 100.0) 
                    total_capacity_pct += cap
                    data_points += 1
            else:
                offline_units += 1

        avg_load = (total_load_pct / data_points) if data_points > 0 else 0
        avg_cap = (total_capacity_pct / data_points) if data_points > 0 else 0

        print("\n" + "="*30)
        report = (
            f"--- UPS WEEKLY STATUS REPORT ---\n"
            f"Total Inventory: {total_units}\n"
            f"Status: {online_units} Online / {offline_units} Offline\n"
            f"Avg Output Load: {avg_load:.1f}%\n"
            f"Avg Battery Capacity: {avg_cap:.1f}%\n"
            f"Metric Success: {data_points}/{online_units} units\n"
            f"--------------------------"
        )
        return report

    except Exception as e:
        return f"\nError parsing UPS data: {str(e)}"

if __name__ == "__main__":
    print(get_ups_status())
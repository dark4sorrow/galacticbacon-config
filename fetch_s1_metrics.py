import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# Paths based on GalacticBacon directory structure
S1_DIR = "/home/damurphy/docker_apps/sentinelone"
DATA_FILE = os.path.join(S1_DIR, "s1_full_inventory.csv")
THREATS_FILE = os.path.join(S1_DIR, "s1_threats.csv")

def get_s1_metrics():
    if not os.path.exists(DATA_FILE):
        return "Error: s1_full_inventory.csv not found."

    try:
        # --- FLEET HEALTH ---
        df = pd.read_csv(DATA_FILE)
        total_agents = len(df)
        win_count = len(df[df['OS'].str.contains("Windows", na=False)])
        mac_count = len(df[df['OS'].str.contains("macOS", na=False)])
        lin_count = len(df[df['OS'].str.contains("Linux", na=False)])
        
        outdated = len(df[df['Status'] == 'OUTDATED'])
        compliance_rate = ((total_agents - outdated) / total_agents * 100) if total_agents > 0 else 0
        
        # --- THREAT ANALYSIS ---
        threat_summary = "No threat data available."
        if os.path.exists(THREATS_FILE):
            df_threats = pd.read_csv(THREATS_FILE)
            if not df_threats.empty and 'Created At' in df_threats.columns:
                # Localize to UTC to match dashboard.py logic
                df_threats['Created At'] = pd.to_datetime(df_threats['Created At'], errors='coerce')
                if df_threats['Created At'].dt.tz is None:
                    df_threats['Created At'] = df_threats['Created At'].dt.tz_localize('UTC')
                
                # Make the comparison timezone-aware
                now_utc = datetime.now(timezone.utc)
                seven_days_ago = now_utc - timedelta(days=7)
                
                recent_threats = df_threats[df_threats['Created At'] >= seven_days_ago]
                
                total_threats = len(recent_threats)
                # Filter out False Positives per dashboard.py logic
                real_threats = recent_threats[recent_threats['Analyst Verdict'] != 'false_positive']
                mitigated = len(real_threats[real_threats['Status'].isin(['mitigated', 'remediated', 'resolved'])])
                active_risks = len(real_threats) - mitigated
                
                threat_summary = f"{total_threats} Total | {mitigated} Mitigated | {active_risks} Active Risks"

        scan_time = datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).strftime('%Y-%m-%d %H:%M')

        report = (
            f"--- SENTINELONE WEEKLY STATUS ---\n"
            f"Inventory Date: {scan_time}\n"
            f"Total Protected Endpoints: {total_agents}\n"
            f"OS Distribution: {win_count} Win | {mac_count} Mac | {lin_count} Lin\n"
            f"Compliance: {compliance_rate:.1f}% ({outdated} Outdated)\n"
            f"Threats (Last 7 Days): {threat_summary}\n"
            f"--------------------------------"
        )
        return report

    except Exception as e:
        return f"Error parsing S1 data: {str(e)}"

if __name__ == "__main__":
    print(get_s1_metrics())
#!/bin/bash

# Mapping Container Names to Repo Paths
declare -A repo_map=(
    ["nmap-web-nse"]="$HOME/nmap-web-nse"
    ["os-fingerprinter-v2"]="$HOME/docker_apps/os-fingerprint"
    ["host-monitor"]="$HOME/docker_apps/host-monitor"
    ["informacast_dash"]="$HOME/docker_apps/informacast"
    ["dns_resolver"]="$HOME/docker_apps/dns"
)

echo "GalacticBacon Integrated Fleet Status"
echo "---------------------------------------"

# Function to check git status
check_git() {
    local path=$1
    if [ -z "$path" ] || [ ! -d "$path/.git" ]; then
        echo -e "\033[0;90m<-- no repo assigned\033[0m"
    else
        if [ -n "$(git -C "$path" status --porcelain)" ]; then
            echo -e "\033[1;33m<-- PENDING COMMITS\033[0m"
        else
            echo -e "\033[0;36m<-- synced\033[0m"
        fi
    fi
}

# List of containers to display
# format: "ContainerName | Port | ExtraInfo"
containers=(
    "it-tools|8081|"
    "openspeedtest|8082|"
    "nmap-web-nse|8084|"
    "os-fingerprinter-v2|8085|"
    "host-monitor|5005| - Last Scan: ${LAST_SCAN_TIME:-No Data}"
    "informacast_dash|5082|"
    "code-server|8778|"
    "secure_firefox|6901|"
    "borg-repo-server|8022|"
    "borg-ui-client|8086|"
)

for item in "${containers[@]}"; do
    IFS='|' read -r name port extra <<< "$item"
    
    # Check if container is running
    if [ "$(sudo docker ps -q -f name=^/${name}$)" ]; then
        status_msg="\033[0;32m[  UP  ]\033[0m"
    else
        status_msg="\033[0;31m[ DOWN ]\033[0m"
    fi

    git_status=$(check_git "${repo_map[$name]}")
    
    printf "%b %-20s (Port: %s)%s %b\n" "$status_msg" "$name" "$port" "$extra" "$git_status"
done

echo "---------------------------------------"

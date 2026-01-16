#!/bin/bash
repos=(
    "~/ups_project"
    "~/nmap-web-nse"
    "~/docker_apps/dns"
    "~/docker_apps/host-monitor"
    "~/docker_apps/informacast"
    "~/docker_apps/os-fingerprint"
)

for repo in "${repos[@]}"; do
    eval cd $repo
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "\033[33m[!] Changes pending in: $repo\033[0m"
    else
        echo -e "\033[32m[✓] Clean: $repo\033[0m"
    fi
done

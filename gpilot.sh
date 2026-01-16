#!/bin/bash

# Configuration: Add your repo paths here
declare -A repos=(
    ["UPS Project"]="$HOME/ups_project"
    ["Nmap Web NSE"]="$HOME/nmap-web-nse"
    ["DNS Resolver"]="$HOME/docker_apps/dns"
    ["Host Monitor"]="$HOME/docker_apps/host-monitor"
    ["Informacast Monitor"]="$HOME/docker_apps/informacast"
    ["OS Fingerprinter"]="$HOME/docker_apps/os-fingerprint"
    ["GalacticBacon Docker"]="$HOME/docker_apps"
)

echo "------------------------------------------"
echo "   GALACTICBACON GIT PILOT [dark4sorrow]  "
echo "------------------------------------------"

# Create a menu from the keys
PS3="Select a repository to push: "
select repo_name in "${!repos[@]}" "Exit"; do
    case $repo_name in
        "Exit")
            echo "Exiting Pilot."
            break
            ;;
        *)
            if [ -n "$repo_name" ]; then
                repo_path="${repos[$repo_name]}"
                echo -e "\nTargeting: $repo_name ($repo_path)"
                
                cd "$repo_path" || { echo "Error: Path not found!"; continue; }

                # Check for changes
                if [ -z "$(git status --porcelain)" ]; then
                    echo "No changes detected. Everything is clean."
                else
                    echo "Changes found. Enter your commit message:"
                    read -r commit_msg
                    
                    if [ -z "$commit_msg" ]; then
                        commit_msg="Update via Git Pilot"
                    fi

                    echo "Syncing to dark4sorrow/GitHub..."
                    git add .
                    git commit -m "$commit_msg"
                    git push
                    echo -e "\n[✓] Push Complete."
                fi
                break
            else
                echo "Invalid selection."
            fi
            ;;
    esac
done

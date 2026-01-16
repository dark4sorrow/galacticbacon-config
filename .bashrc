# ~/.bashrc: GalacticBacon Config (v0.0.89) - Git, Management & SSL Audit

case $- in
    *i*) ;;
      *) return;;
esac

HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s checkwinsize
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# Set base colors
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# Function to pull git branch status for the prompt
parse_git_bg() {
  local branch=$(git branch 2>/dev/null | grep '^*' | colrm 1 2)
  if [ -n "$branch" ]; then
    local status=$(git status --porcelain 2>/dev/null)
    if [ -n "$status" ]; then
      # Yellow if there are uncommitted changes
      echo -e " \001\033[33m\002($branch*)\001\033[00m\002"
    else
      # Cyan if everything is clean
      echo -e " \001\033[36m\002($branch)\001\033[00m\002"
    fi
  fi
}

# Define the Prompt
if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]$(parse_git_bg)\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w$(parse_git_bg)\$ '
fi
unset color_prompt force_color_prompt

case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
esac

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

if [ -f ~/.bash_aliases ]; then . ~/.bash_aliases; fi

if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# --- GalacticBacon Management Suite ---
unalias fleet 2>/dev/null; unalias toolbox 2>/dev/null; unalias refresh 2>/dev/null
unset -f fleet 2>/dev/null; unset -f toolbox 2>/dev/null; unset -f refresh 2>/dev/null

fleet() {
    clear
    toolbox
    echo -e "\n\033[1m🛰️  Following Fleet Logs (Ctrl+C to exit)...\033[0m\n"
    sudo docker logs -f --tail 20 host-monitor &
    cd ~/docker_apps && docker compose logs -f --tail 20
}

toolbox() {
    clear
    # 1. Host Monitor Data Extraction
    local DATA_FILE=~/docker_apps/host-monitor/output/hosts_data.json
    if [ -f "$DATA_FILE" ]; then
        export LAST_SCAN_TIME=$(grep -oP '"last_updated": "\K[^"]+' "$DATA_FILE")
    else
        export LAST_SCAN_TIME="No Data"
    fi

    # 2. SSL Status Audit (Live)
    local SSL_DOMAIN="galacticbacon.nic.edu"
    local SSL_EXP_DATE=$(echo | openssl s_client -connect ${SSL_DOMAIN}:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d'=' -f2)
    local SSL_REMAINING=$(( ( $(date -d "$SSL_EXP_DATE" +%s) - $(date +%s) ) / 86400 ))
    
    if [ "$SSL_REMAINING" -lt 15 ]; then
        local SSL_COLOR='\033[01;31m' # Red Alert
    else
        local SSL_COLOR='\033[01;32m' # Green OK
    fi

    # 3. Display Integrated Fleet (via ds.sh)
    if [ -f ~/ds.sh ]; then 
        bash ~/ds.sh
    else 
        echo "⚠️ ds.sh not found."
    fi
    
    # 4. Command Menu & Final Telemetry
    local BLUE='\033[01;34m'
    local NC='\033[0m'
    
    echo -e "CMDS: ${BLUE}toolbox${NC} | ${BLUE}refresh${NC} | ${BLUE}fleet${NC} | ${BLUE}gpilot${NC} | ${BLUE}gsave${NC} |"
    echo -e "SSL STATUS [${SSL_DOMAIN}]: ${SSL_COLOR}${SSL_REMAINING} days remaining${NC} ($SSL_EXP_DATE)"
    echo "System Time: $(date)"
}

refresh() {
    echo "🚀 Rebuilding Galactic Host Monitor (v0.0.85)..."
    cd ~/docker_apps/host-monitor || { echo "❌ Folder not found!"; return; }
    
    sudo mkdir -p output && sudo chmod 777 output
    sudo docker network create galactic-net 2>/dev/null || true
    sudo docker network connect galactic-net swag 2>/dev/null || true
    
    sudo docker build -t galactic-monitor .
    sudo docker stop host-monitor || true && sudo docker rm host-monitor || true
    
    sudo docker run -d \
      --name host-monitor \
      --network galactic-net \
      -p 5005:5000 \
      -v $(pwd)/config.json:/app/config.json \
      -v $(pwd)/output:/app/output \
      --restart unless-stopped \
      -e PYTHONUNBUFFERED=1 \
      galactic-monitor gunicorn --bind 0.0.0.0:5000 --timeout 120 --workers 2 --access-logfile - --error-logfile - app:app
    
    sudo docker image prune -f
    sleep 2
    sudo chown -R $USER:$USER output/
    
    echo "✅ Rebuild complete."
    toolbox
}

# Auto-run toolbox on login if ds.sh exists
if [ -f ~/ds.sh ]; then toolbox; fi

# Aliases
alias gsave='git add . && git commit -m "Quick save via alias" && git push'
alias gpilot='~/gpilot.sh'
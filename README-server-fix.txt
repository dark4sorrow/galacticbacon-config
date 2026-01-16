===================================================================
 GALACTICBACON SERVER RECOVERY NOTES - DEC 13, 2025
===================================================================

ISSUE:
Server crashed; Nginx failed on reboot because SSL certs in /tmp/ were wiped.

FIX:
1. Moved SSL storage from /tmp/ to /etc/nginx/ssl/ (Permanent).
2. Regenerated Tailscale cert for "galacticbacon.ocelot-daggertooth.ts.net".
3. Updated Nginx config to point to new permanent paths.
4. Created automated renewal script (Tailscale certs expire ~90 days).

KEY PATHS:
- SSL Directory:       /etc/nginx/ssl/
- Cert File:           /etc/nginx/ssl/galacticbacon.ocelot-daggertooth.ts.net.crt
- Key File:            /etc/nginx/ssl/galacticbacon.ocelot-daggertooth.ts.net.key
- Nginx Config:        /etc/nginx/sites-available/ups-dashboard
- Renewal Script:      /etc/nginx/ssl/renew_cert.sh
- Renewal Log:         /var/log/tailscale_cert_renew.log

AUTOMATION (CRON):
- Schedule: Every Monday at 4:00 AM
- Command:  /etc/nginx/ssl/renew_cert.sh

USEFUL COMMANDS:
- Check Nginx Status:  sudo systemctl status nginx
- Test Nginx Config:   sudo nginx -t
- Restart Nginx:       sudo systemctl restart nginx
- Manually Renew Cert: sudo /etc/nginx/ssl/renew_cert.sh
- Edit Renewal Job:    sudo crontab -e
- Restart Python App:  sudo systemctl restart ups-dashboard
- View App Logs:       sudo journalctl -u ups-dashboard -f

DOMAINS:
- Internal Access:     https://galacticbacon.nic.edu (Browser Warning: YES)
- Tailscale Access:    https://galacticbacon.ocelot-daggertooth.ts.net
- Cockpit:             https://galacticbacon.nic.edu/cockpit/

===================================================================

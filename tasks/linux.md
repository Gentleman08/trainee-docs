Create a service and add it to systemd that starts a basic node js hello world app.
 
If the node app process crashes or terminates -> the system service added to systemd should automatically restart it 
 
use nginx as a reverse proxy to point all incoming traffic to the node app

## AI-generated: Systemd + Nginx setup (concise)

### Overview

- Run a simple Node.js app as a systemd service and have `nginx` reverse-proxy HTTP traffic to it.

### Files to create

- Minimal Node app: `app.js`
- Systemd unit: `/etc/systemd/system/nodeapp.service`
- Nginx site: `/etc/nginx/sites-available/nodeapp` (symlink to `sites-enabled`)

### Example Node app (app.js)

```js
const http = require('http');
const PORT = process.env.PORT || 3000;
http.createServer((req, res) => {
	res.writeHead(200, {'Content-Type': 'text/plain'});
	res.end('Hello from Node.js\n');
}).listen(PORT, () => console.log(`Listening on ${PORT}`));
```

### Example systemd unit (`nodeapp.service`)

```ini
[Unit]
Description=Node.js Hello App
After=network.target

[Service]
User=www-data
Environment=PORT=3000
WorkingDirectory=/opt/nodeapp
ExecStart=/usr/bin/node /opt/nodeapp/app.js
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=nodeapp

[Install]
WantedBy=multi-user.target
```

Commands to enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nodeapp.service
sudo systemctl status nodeapp.service
```

### Example nginx reverse-proxy configuration

```nginx
server {
		listen 80;
		server_name example.com; # replace with your domain or IP

		location / {
				proxy_pass http://127.0.0.1:3000;
				proxy_http_version 1.1;
				proxy_set_header Upgrade $http_upgrade;
				proxy_set_header Connection 'upgrade';
				proxy_set_header Host $host;
				proxy_cache_bypass $http_upgrade;
		}
}
```

Commands to enable nginx site and reload:

```bash
sudo ln -s /etc/nginx/sites-available/nodeapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Verification

```bash
curl -I http://localhost:3000    # direct to Node app
curl -I http://localhost         # via nginx
sudo journalctl -u nodeapp -f    # follow logs
```

### Notes & tips

- Ensure `/opt/nodeapp` exists and contains `app.js` and any `package.json` dependencies.
- Run `npm install --production` in `/opt/nodeapp` as the deployment user before starting.
- Use a non-root system user (e.g., `www-data` or custom) for the service.
- Consider adding a firewall rule to allow HTTP only and block direct app port if desired.

---

_This appended section is AI-generated and intended as a concise practical reference._
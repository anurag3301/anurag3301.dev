# Setup the project on VPS
```sh
# clone the repo
git clone https://github.com/anurag3301/anurag3301.dev.git

cd anurag3301.dev

# Install deps
sudo apt install python3-pip 
pip install -r requirements.txt --break-system-packages

# setup Caddy for reverse proxy and https
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
sudo sh -c 'cat > /etc/caddy/Caddyfile <<EOF
anurag3301.dev, www.anurag3301.dev {
    reverse_proxy 127.0.0.1:5000
}
EOF'
sudo systemctl restart caddy

# run `sudo visudo` and add following, replace the username if its something else
anurag ALL=NOPASSWD: /bin/systemctl status webserver
anurag ALL=NOPASSWD: /bin/systemctl restart webserver

# setup init script for the server
sudo sh -c "cat > /etc/systemd/system/webserver.service <<EOF
[Unit]
Description=anurag3301.dev webserver
After=network.target

[Service]
User=$(id -nu 1000)
Group=$(id -ng 1000)
WorkingDirectory=$(pwd)
ExecStart=$(eval echo ~$(id -nu 1000))/.local/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable webserver
sudo systemctl start webserver
```

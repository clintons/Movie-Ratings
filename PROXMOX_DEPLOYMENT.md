# Deploying to Proxmox LXC Container

## Quick Deployment Guide

### Step 1: Create LXC Container in Proxmox

1. In Proxmox web interface, click "Create CT"
2. Configure:
   - **Hostname**: movie-ratings
   - **Template**: ubuntu-22.04 or ubuntu-24.04
   - **Root password**: Set a secure password
   - **Disk**: 10GB minimum
   - **CPU**: 2 cores
   - **Memory**: 2048 MB
   - **Network**: Bridge, DHCP or static IP

3. **Important**: Enable nesting for Docker support
   - In Container Options → Features
   - Check "Nesting"
   - OR via command line:
     ```bash
     pct set <CTID> -features nesting=1
     ```

### Step 2: Install Docker in LXC

SSH into your LXC container and run:

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to docker group (if not root)
usermod -aG docker $USER

# Install Docker Compose
apt install -y docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 3: Transfer Application Files

From your local machine, transfer the entire project:

```bash
# If using SCP
scp -r movie-ratings-app/ root@<LXC-IP>:/opt/

# Or use rsync
rsync -avz movie-ratings-app/ root@<LXC-IP>:/opt/movie-ratings-app/
```

Alternatively, clone from a Git repository:

```bash
# On the LXC
cd /opt
git clone <your-repo-url> movie-ratings-app
```

### Step 4: Prepare Your Data

Copy your Excel file to the container:

```bash
# From local machine
scp "Movie Ratings.xlsx" root@<LXC-IP>:/opt/movie-ratings-app/data/

# Or on the LXC, mount a shared folder
# Edit /etc/pve/lxc/<CTID>.conf and add:
# mp0: /path/on/host,mp=/mnt/data
```

### Step 5: Configure and Start

On the LXC container:

```bash
cd /opt/movie-ratings-app

# Copy and edit environment file
cp .env.example .env
nano .env  # Add your OMDB API key

# Ensure Excel file is in place
ls -la data/

# Start the application
./start.sh

# Or manually:
docker-compose up -d
```

### Step 6: Access the Application

Find your LXC IP address:

```bash
ip addr show eth0
```

Access the app at: `http://<LXC-IP>:5000`

### Step 7: (Optional) Set Up Reverse Proxy

For production use with a domain name, set up NGINX:

```bash
# Install NGINX on LXC or separate container
apt install -y nginx

# Create NGINX config
cat > /etc/nginx/sites-available/movie-ratings << 'EOF'
server {
    listen 80;
    server_name movies.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        proxy_pass http://localhost:5000/static;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/movie-ratings /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 8: Enable Auto-Start on Boot

```bash
# Docker auto-start
systemctl enable docker

# Application auto-start via systemd
cat > /etc/systemd/system/movie-ratings.service << 'EOF'
[Unit]
Description=Movie Ratings Web App
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/movie-ratings-app
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable movie-ratings
systemctl start movie-ratings
```

## Maintenance Commands

```bash
# View logs
cd /opt/movie-ratings-app
docker-compose logs -f

# Restart application
docker-compose restart

# Update application
git pull  # if using git
docker-compose up -d --build

# Backup database
docker-compose exec db pg_dump -U postgres movieratings > backup-$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U postgres movieratings < backup.sql

# Fetch all movie posters
docker-compose exec web python /app/fetch_posters.py
```

## Troubleshooting

### Container won't start
```bash
# Check LXC nesting is enabled
pct config <CTID> | grep features

# Check Docker status
systemctl status docker
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Port already in use
```bash
# Change port in docker-compose.yml
nano /opt/movie-ratings-app/docker-compose.yml
# Change "5000:5000" to "8080:5000"
docker-compose up -d
```

### Excel import failed
```bash
# Check file location
ls -la /opt/movie-ratings-app/data/

# View import logs
docker-compose logs web | grep -i import

# Manual import
docker-compose exec web python /app/init_db.py /app/data/Movie\ Ratings.xlsx
```

## Security Recommendations

1. **Change default passwords**:
   - Edit `.env` and change PostgreSQL password
   - Never use default passwords in production

2. **Firewall**:
   ```bash
   # Only allow from your network
   ufw allow from 192.168.1.0/24 to any port 5000
   ufw enable
   ```

3. **HTTPS with Let's Encrypt** (if using domain):
   ```bash
   apt install certbot python3-certbot-nginx
   certbot --nginx -d movies.yourdomain.com
   ```

4. **Regular backups**:
   - Set up cron job for database backups
   - Backup posters directory
   - Store backups off-site

## Resource Usage

Typical resource consumption:
- **RAM**: ~500MB (database + web app)
- **Disk**: ~5GB (with posters)
- **CPU**: Minimal (<5% idle)

Adjust LXC resources if needed:
```bash
# On Proxmox host
pct set <CTID> -memory 4096 -cores 4
```

---

You now have a fully functional movie ratings web app running in a Proxmox LXC container!

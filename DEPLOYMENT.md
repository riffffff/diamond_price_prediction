# 🚀 Deployment Guide - Diamond Price Prediction

Panduan lengkap untuk deploy aplikasi ke VPS menggunakan Docker Compose + Nginx + SSL.

## 📋 Prerequisites

- VPS dengan Ubuntu 22.04/24.04 (minimal 2GB RAM, 2 vCPU)
- Domain yang sudah dipointing ke IP VPS
- Docker & Docker Compose sudah terinstall
- Git terinstall di VPS

## 🔧 Setup VPS (One-time)

### 1. Update System & Install Dependencies

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y ca-certificates curl gnupg lsb-release git ufw

# Setup firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Install Docker & Docker Compose

```bash
# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (logout and login again after this)
sudo usermod -aG docker $USER

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Verify installation
docker --version
docker compose version
```

### 3. Create Application Directory

```bash
# Create directory for application
sudo mkdir -p /opt/diamond_app
sudo chown $USER:$USER /opt/diamond_app
```

## 📦 Deploy Application

### 1. Clone Repository

```bash
cd /opt/diamond_app
git clone https://github.com/riffffff/diamond_price_prediction.git .
```

### 2. Upload Model Files

**From your local machine** (in project directory):

```bash
# Upload model files to VPS
scp -r saved_model/ USERNAME@YOUR_VPS_IP:/opt/diamond_app/

# Or use rsync (recommended)
rsync -avP saved_model/ USERNAME@YOUR_VPS_IP:/opt/diamond_app/saved_model/
```

Verify on VPS:
```bash
ls -lh /opt/diamond_app/saved_model/
# Should see: model.pkl and features.pkl
```

### 3. Configure Domain

Edit nginx configuration:

```bash
cd /opt/diamond_app
nano deploy/nginx.conf
```

Replace `YOUR_DOMAIN.com` with your actual domain in all locations.

### 4. Start Services (HTTP only, first time)

```bash
cd /opt/diamond_app

# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Check service status
docker compose -f docker-compose.prod.yml ps
```

Wait for all services to be healthy, then test:
- Visit: `http://YOUR_DOMAIN.com` → Should see Streamlit UI
- Test API: `curl http://YOUR_DOMAIN.com/predict` (might return error without POST data, that's OK)

### 5. Setup SSL Certificate (Let's Encrypt)

Once HTTP is working:

```bash
cd /opt/diamond_app

# Make script executable
chmod +x deploy/setup-ssl.sh

# Run SSL setup (replace with your domain and email)
./deploy/setup-ssl.sh your-domain.com your-email@example.com
```

After certificate is obtained, follow the instructions printed by the script:

1. Edit `deploy/nginx.conf`:
   - Uncomment the HTTPS server block (lines starting with `# server { listen 443...`)
   - Uncomment the HTTP redirect block (redirect HTTP → HTTPS)
   - Replace `YOUR_DOMAIN.com` with your actual domain

2. Restart nginx:
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

3. Test HTTPS:
   - Visit: `https://YOUR_DOMAIN.com`

### 6. Setup Auto-renewal for SSL (Optional but recommended)

The certbot container will automatically renew certificates. Verify:

```bash
# Check certbot container logs
docker logs diamond_certbot

# Manually test renewal (dry run)
docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run
```

## 🔄 Update Deployment

When you have new code changes:

```bash
cd /opt/diamond_app

# Pull latest code
git pull origin main

# Rebuild and restart services
docker compose -f docker-compose.prod.yml up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f --tail 100
```

## 📊 Monitoring & Maintenance

### Check Service Status

```bash
# Check all containers
docker compose -f docker-compose.prod.yml ps

# Check specific service logs
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs streamlit
docker compose -f docker-compose.prod.yml logs nginx

# Follow logs in real-time
docker compose -f docker-compose.prod.yml logs -f
```

### Restart Services

```bash
# Restart all services
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart api
docker compose -f docker-compose.prod.yml restart streamlit
docker compose -f docker-compose.prod.yml restart nginx
```

### Stop Services

```bash
# Stop all services
docker compose -f docker-compose.prod.yml down

# Stop and remove volumes (careful!)
docker compose -f docker-compose.prod.yml down -v
```

### View Resource Usage

```bash
# Check container resource usage
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Backup Model Files

```bash
# Backup model files
cd /opt/diamond_app
tar -czf saved_model_backup_$(date +%Y%m%d).tar.gz saved_model/

# Download backup to local machine (from local)
scp USERNAME@YOUR_VPS_IP:/opt/diamond_app/saved_model_backup_*.tar.gz ./
```

## 🐛 Troubleshooting

### Services not starting

```bash
# Check container logs
docker compose -f docker-compose.prod.yml logs

# Check if ports are already in use
sudo netstat -tulpn | grep -E ':(80|443|5000|8501)'

# Rebuild from scratch
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build --force-recreate
```

### API returns 500 error

```bash
# Check API logs
docker compose -f docker-compose.prod.yml logs api

# Verify model files exist
docker compose -f docker-compose.prod.yml exec api ls -lh /saved_model/

# Restart API
docker compose -f docker-compose.prod.yml restart api
```

### Streamlit not loading

```bash
# Check Streamlit logs
docker compose -f docker-compose.prod.yml logs streamlit

# Check if API is reachable from Streamlit container
docker compose -f docker-compose.prod.yml exec streamlit curl http://api:5000/

# Restart Streamlit
docker compose -f docker-compose.prod.yml restart streamlit
```

### SSL certificate issues

```bash
# Check certbot logs
docker logs diamond_certbot

# Check certificate expiry
docker compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renew certificate
docker compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart nginx
```

### Nginx configuration errors

```bash
# Test nginx configuration
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# View nginx error logs
docker compose -f docker-compose.prod.yml exec nginx cat /var/log/nginx/error.log
```

## 🔒 Security Recommendations

1. **Firewall**: Only allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
2. **SSH**: Use SSH keys instead of passwords
3. **Updates**: Regularly update system packages and Docker images
4. **Backups**: Regular backups of model files and data
5. **Monitoring**: Set up monitoring alerts for service downtime

## 📝 Quick Reference Commands

```bash
# Start services
docker compose -f docker-compose.prod.yml up -d

# Stop services
docker compose -f docker-compose.prod.yml down

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart all
docker compose -f docker-compose.prod.yml restart

# Update and redeploy
git pull && docker compose -f docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker-compose.prod.yml ps
```

## 🎯 Architecture

```
Internet
    ↓
[Nginx Container :80/:443]
    ↓
    ├─→ [Streamlit Container :8501] → Main UI
    └─→ [API Container :5000] → /predict endpoint
            ↓
        [saved_model/] volume
```

## 📞 Support

If you encounter issues:
1. Check logs first: `docker compose -f docker-compose.prod.yml logs`
2. Verify all containers are running: `docker compose -f docker-compose.prod.yml ps`
3. Check firewall: `sudo ufw status`
4. Verify DNS: `nslookup YOUR_DOMAIN.com`

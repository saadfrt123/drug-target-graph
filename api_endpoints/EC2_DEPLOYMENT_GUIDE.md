# 🚀 EC2 Deployment Guide for FastAPI Endpoints

## 📋 Overview

This guide walks you through deploying the Drug-Target Graph FastAPI endpoints on an AWS EC2 instance.

**⚠️ Important:** This deployment guide covers the **SIMPLIFIED FastAPI design** with **4-5 AI-only endpoints**.  
- For the full API design (35+ endpoints), see `API_ENDPOINTS_DOCUMENTATION.md`  
- See `SIMPLIFIED_DESIGN.md` for architecture details

**Endpoints being deployed:**
1. `GET /health` - Health check
2. `POST /classification/classify` - AI classification (single)
3. `POST /classification/batch` - AI classification (batch)
4. `POST /cascade/predict` - AI cascade prediction
5. `GET /classification/status/{drug}/{target}` - Status check (optional)

---

## 🔧 Prerequisites

### What You Need Before Starting:

1. **AWS Account** with EC2 access
2. **Neo4j Database** (can be Aura, self-hosted, or EC2-deployed)
3. **Gemini API Key** for AI classification/prediction features
4. **Domain Name** (optional, for custom subdomain)
5. **SSH Key Pair** for EC2 access

---

## 📦 Infrastructure Requirements

### EC2 Instance Specs:

**Recommended:** `t3.medium` or `t3.large`
- **vCPUs:** 2-4
- **RAM:** 4-8 GB
- **Storage:** 20-50 GB (SSD)
- **OS:** Ubuntu 22.04 LTS or Amazon Linux 2023

**Rationale:**
- Handles concurrent API requests
- Sufficient memory for Gemini API calls
- Fast disk I/O for Neo4j caching

### Network Configuration:

**Security Group Rules:**
```
Inbound:
  - Port 80 (HTTP) - 0.0.0.0/0
  - Port 443 (HTTPS) - 0.0.0.0/0
  - Port 22 (SSH) - Your IP only
  
Outbound:
  - All traffic (for Neo4j and Gemini API calls)
```

---

## 🔐 Environment Variables

### Required Environment Variables:

Create a `.env` file on EC2:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j

# Gemini API
GEMINI_API_KEY=your_gemini_key_here

# FastAPI Configuration
ENVIRONMENT=production
DEBUG=False

# Security
API_KEY=generate_a_secure_random_key_here
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Optional: Redis for caching
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 🛠️ Step-by-Step Deployment

### Phase 1: EC2 Instance Setup

#### 1. Launch EC2 Instance

```bash
# Via AWS Console:
1. Go to EC2 → Launch Instance
2. Choose Ubuntu 22.04 LTS
3. Select t3.medium
4. Create/select key pair
5. Configure security group (ports 22, 80, 443)
6. Launch instance
```

#### 2. Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### 3. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

---

### Phase 2: Install Dependencies

#### 1. Install Python 3.11+

```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
```

#### 2. Install System Dependencies

```bash
# For Neo4j driver
sudo apt install -y gcc python3.11-dev

# For process management
sudo apt install -y nginx supervisor

# For SSL certificates
sudo apt install -y certbot python3-certbot-nginx
```

#### 3. Install Redis (Optional - for caching)

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

---

### Phase 3: Deploy Application Code

#### 1. Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/your-org/drug-target-graph.git
cd drug-target-graph/api_endpoints
```

#### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your values
nano .env

# Or use AWS Systems Manager Parameter Store (recommended)
# Store secrets securely in AWS SSM
```

---

### Phase 4: Configure FastAPI Application

#### 1. Use Complete Implementation

**🎯 IMPORTANT:** Use the complete implementation provided in `FASTAPI_IMPLEMENTATION_GUIDE.md`!

The deployment guide includes placeholder code. For production-ready code:
- See: `FASTAPI_IMPLEMENTATION_GUIDE.md` - **Complete working code with all endpoints**
- Copy `main.py`, `config.py`, `requirements.txt` from that guide
- The guide includes all 5 endpoints with proper error handling, logging, and authentication

#### 2. Test Application Locally

```bash
# Run development server
uvicorn main:app --host 0.0.0.0 --port 8000

# Test from another terminal
curl http://localhost:8000/health
```

---

### Phase 5: Production Server Setup

#### 1. Install Gunicorn + Uvicorn Workers

```bash
pip install gunicorn uvloop httptools
```

#### 2. Create Gunicorn Configuration

Create `api_endpoints/gunicorn_config.py`:

```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "drug-target-api"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
umask = 0
user = "ubuntu"
group = "ubuntu"
tmp_upload_dir = None
```

#### 3. Create Systemd Service

Create `/etc/systemd/system/drug-target-api.service`:

```ini
[Unit]
Description=Drug-Target Graph FastAPI Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/drug-target-graph/api_endpoints
Environment="PATH=/home/ubuntu/drug-target-graph/api_endpoints/venv/bin"
ExecStart=/home/ubuntu/drug-target-graph/api_endpoints/venv/bin/gunicorn main:app -c gunicorn_config.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Start and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable drug-target-api
sudo systemctl start drug-target-api
sudo systemctl status drug-target-api
```

---

### Phase 6: Nginx Reverse Proxy

#### 1. Create Nginx Configuration

Create `/etc/nginx/sites-available/drug-target-api`:

```nginx
upstream drug_target_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;  # or EC2 public IP

    # Logging
    access_log /var/log/nginx/drug-target-access.log;
    error_log /var/log/nginx/drug-target-error.log;

    # Client body size
    client_max_body_size 10M;

    location / {
        proxy_pass http://drug_target_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://drug_target_api;
        access_log off;
    }
}
```

#### 2. Enable and Restart Nginx

```bash
sudo ln -s /etc/nginx/sites-available/drug-target-api /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

---

### Phase 7: SSL/TLS Setup (HTTPS)

#### 1. Get SSL Certificate

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### 2. Auto-Renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot auto-renews via systemd timer (already enabled)
```

---

### Phase 8: Monitoring & Logging

#### 1. Set Up Log Rotation

Create `/etc/logrotate.d/drug-target-api`:

```
/var/log/gunicorn/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload drug-target-api
    endscript
}
```

#### 2. Install Monitoring Tools

```bash
# Install AWS CloudWatch Agent (optional)
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Or use simple monitoring
sudo apt install -y htop iotop
```

#### 3. Set Up Uptime Monitoring

```bash
# Create simple health check script
cat > /home/ubuntu/healthcheck.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:8000/health || systemctl restart drug-target-api
EOF

chmod +x /home/ubuntu/healthcheck.sh

# Add to crontab (runs every 5 minutes)
crontab -e
# Add: */5 * * * * /home/ubuntu/healthcheck.sh
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Disable Root Login

```bash
# Edit /etc/ssh/sshd_config
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

sudo systemctl restart ssh
```

### 3. Fail2Ban Setup

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 Cost Estimation

### Monthly EC2 Costs (Approximate):

| Component | Instance Type | Monthly Cost |
|-----------|--------------|--------------|
| EC2 Instance | t3.medium | ~$30 |
| Data Transfer (10GB) | - | ~$1 |
| Storage (30GB EBS) | gp3 | ~$3 |
| Elastic IP | - | Free |
| SSL Certificate | Let's Encrypt | Free |
| **Total** | | **~$34/month** |

### Optional Costs:

| Service | Monthly Cost |
|---------|--------------|
| CloudWatch Monitoring | ~$10 |
| Load Balancer (ALB) | ~$20 |
| Route53 DNS | ~$0.50 |
| S3 for Logs | ~$2 |

---

## 🎯 Quick Deployment Checklist

- [ ] Launch EC2 instance (Ubuntu 22.04, t3.medium)
- [ ] Configure security group (ports 22, 80, 443)
- [ ] SSH into instance
- [ ] Install Python 3.11+, Nginx, Supervisor
- [ ] Clone repository
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure `.env` file
- [ ] Test FastAPI app locally
- [ ] Set up systemd service
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificate
- [ ] Configure firewall
- [ ] Set up monitoring/logging
- [ ] Test all endpoints
- [ ] Document API endpoints
- [ ] Set up automated backups
- [ ] Configure CloudWatch alarms

---

## 🧪 Post-Deployment Testing

### 1. Health Check

```bash
curl https://your-domain.com/health
# Expected: {"status": "healthy", "service": "drug-target-api"}
```

### 2. Test Protected Endpoint

```bash
curl -X POST https://your-domain.com/api/v1/classify \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "aspirin", "target_name": "PTGS1"}'
```

### 3. Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt install -y apache2-utils

# Run load test
ab -n 1000 -c 10 -H "X-API-Key: your_api_key" \
   https://your-domain.com/health
```

---

## 🔄 Maintenance Tasks

### Regular Updates

```bash
# Weekly: Update packages
sudo apt update && sudo apt upgrade -y

# Monthly: Update Python dependencies
cd /home/ubuntu/drug-target-graph/api_endpoints
source venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart drug-target-api
```

### Backup Strategy

```bash
# Backup application code
tar -czf backup-$(date +%Y%m%d).tar.gz \
    /home/ubuntu/drug-target-graph \
    /etc/nginx/sites-available/drug-target-api \
    /etc/systemd/system/drug-target-api.service

# Upload to S3 (if configured)
aws s3 cp backup-*.tar.gz s3://your-backup-bucket/
```

---

## 🚨 Troubleshooting

### Application Not Starting

```bash
# Check logs
sudo journalctl -u drug-target-api -n 100 -f

# Check if port is in use
sudo netstat -tlnp | grep 8000

# Restart service
sudo systemctl restart drug-target-api
```

### Nginx 502 Bad Gateway

```bash
# Check if FastAPI is running
curl http://localhost:8000/health

# Check Nginx error logs
sudo tail -f /var/log/nginx/drug-target-error.log

# Check Gunicorn logs
sudo tail -f /var/log/gunicorn/error.log
```

### Out of Memory

```bash
# Check memory usage
free -h
htop

# Reduce worker count in gunicorn_config.py
# Restart service
sudo systemctl restart drug-target-api
```

---

## 📚 Additional Resources

- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/
- AWS EC2 Documentation: https://docs.aws.amazon.com/ec2/
- Nginx Documentation: https://nginx.org/en/docs/
- Certbot Documentation: https://certbot.eff.org/

---

## ✅ Next Steps After Deployment

1. **Document API endpoints** - Share with frontend team
2. **Set up CI/CD** - Automate deployments
3. **Configure monitoring** - CloudWatch, Datadog, etc.
4. **Load testing** - Test under production load
5. **Backup strategy** - Automated daily backups
6. **Rate limiting** - Implement to prevent abuse
7. **API documentation** - Swagger UI at `/docs`

---

**🎉 Your API should now be live at: `https://your-domain.com`**


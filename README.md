# 🌍 TravelMemory — MERN Stack AWS EC2 Deployment

> A full-stack travel memory application deployed on AWS EC2 with high availability,
> load balancing, custom domain, and SSL via Cloudflare.

---

## 🔗 Live Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend (www) | https://www.draxil.site | React application |
| Root domain | https://draxil.site | Redirects to www |
| Backend API | https://api.draxil.site | Node.js REST API |

---

## 📐 Architecture Diagram

### How Traffic Flows

```
User Browser (HTTPS)
        │
        ▼
Cloudflare — draxil.site
(DNS · SSL Termination · WAF)
        │                    │
  www / root              api subdomain
  A record / CNAME        CNAME record
        │                    │
        ▼                    ▼
TM-Frontend-ALB        TM-Backend-ALB
(AWS App LB)           (AWS App LB)
   │       │               │       │
   ▼       ▼               ▼       ▼
FE-1     FE-2           BE-1     BE-2
React   React         Node.js  Node.js
+Nginx  +Nginx        +PM2     +PM2
                          │
                          ▼
                   MongoDB Atlas
                  (TravelMemoryCluster)
```

---

## 🛠️ Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Node.js | 18.x LTS | Backend runtime |
| Express.js | 4.x | Backend REST API framework |
| React.js | 18.x | Frontend SPA framework |
| MongoDB Atlas | M0 Free | Cloud-hosted database |
| Mongoose | 7.x | MongoDB ODM |
| Nginx | 1.18+ | Web server and reverse proxy |
| PM2 | Latest | Node.js process manager |
| AWS EC2 | t2.micro | Virtual cloud servers |
| AWS ALB | - | Application Load Balancer |
| Ubuntu | 22.04 LTS | Server operating system |
| Cloudflare | Free plan | DNS, SSL, CDN, WAF |

---

## 🏗️ Infrastructure Details

### EC2 Instances

| Instance Name | Type | OS | Role | Security Group |
|--------------|------|----|------|---------------|
| TM-Backend-1 | t2.micro | Ubuntu 22.04 | Node.js API server | TM-Backend-SG |
| TM-Backend-2 | t2.micro | Ubuntu 22.04 | Node.js API server | TM-Backend-SG |
| TM-Frontend-1 | t2.micro | Ubuntu 22.04 | React static files | TM-Frontend-SG |
| TM-Frontend-2 | t2.micro | Ubuntu 22.04 | React static files | TM-Frontend-SG |

### Security Groups

**TM-Backend-SG — Inbound Rules:**

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| SSH | TCP | 22 | My IP only | Secure server access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Nginx receives traffic |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Node.js application |

**TM-Frontend-SG — Inbound Rules:**

| Type | Protocol | Port | Source | Purpose |
|------|----------|------|--------|---------|
| SSH | TCP | 22 | My IP only | Secure server access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Nginx serves React app |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure HTTPS access |

### Load Balancers

| Name | Type | Target Group | DNS Name |
|------|------|-------------|----------|
| TM-Frontend-ALB | Application | TM-Frontend-TG | TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com |
| TM-Backend-ALB | Application | TM-Backend-TG | TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com |

### Cloudflare DNS Records

| Type | Name | Points To | Purpose |
|------|------|-----------|---------|
| A | @ (root) | TM-Frontend-1 Public IP | draxil.site → EC2 directly |
| CNAME | www | TM-Frontend-ALB DNS | www.draxil.site → Frontend ALB |
| CNAME | api | TM-Backend-ALB DNS | api.draxil.site → Backend ALB |

---

## 📸 Deployment Screenshots

All 75 deployment screenshots are stored in the `/screenshots` folder documenting every step.

---

## 📋 Step-by-Step Deployment

### Phase 1 — AWS Initial Setup

**1A. Create Key Pair**

Navigate to: EC2 → Network & Security → Key Pairs → Create key pair

```
Name:   travelmemory-key
Type:   RSA
Format: .pem
```

The `.pem` file downloads automatically. It is the only way to SSH into your servers.

**1B. Create Backend Security Group (TM-Backend-SG)**

Navigate to: EC2 → Security Groups → Create security group

**1C. Create Frontend Security Group (TM-Frontend-SG)**

---

### Phase 2 — MongoDB Atlas Database

1. Created free M0 cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Cluster: `TravelMemoryCluster`, Region: `ap-south-1`
3. Database user: `tmuser` with Atlas admin role
4. Network Access: `0.0.0.0/0` — allows all IP addresses

Connection string format:
```
mongodb+srv://tmuser:<password>@travelmemorycluster.xxxxx.mongodb.net/travelmemory?retryWrites=true&w=majority
```

---

### Phase 3 — Launch 4 EC2 Instances

Each instance created with:
- AMI: **Ubuntu Server 22.04 LTS**
- Type: **t2.micro** (free tier)
- Key pair: **travelmemory-key**
- Storage: 8 GB gp2

---

### Phase 4 — Backend Configuration (TM-Backend-1 and TM-Backend-2)

**SSH into the instance:**
```bash
ssh -i ~/Downloads/travelmemory-key.pem ubuntu@<BACKEND-EC2-PUBLIC-IP>
```

**Install all dependencies:**
```bash
# Update the system
sudo apt update
sudo apt upgrade -y

# Install Node.js 18 (LTS)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version   # v18.x.x
npm --version    # 9.x.x

# Install Git and Nginx
sudo apt install -y git nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Clone the repository:**
```bash
cd ~
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/backend
```

**Install Node.js dependencies:**
```bash
npm install
```

**Create the .env file:**
```bash
nano .env
```

Contents:
```
PORT=3000
MONGO_URI=mongodb+srv://tmuser:TravelMemory@2024@travelmemorycluster.xxxxx.mongodb.net/travelmemory?retryWrites=true&w=majority
```

**Test the server runs:**
```bash
node index.js
# Should show: Server running on port 3000 + MongoDB connected
```

**Start with PM2:**
```bash
sudo npm install -g pm2
pm2 start index.js --name "tm-backend"
pm2 startup
# Run the command PM2 outputs above
pm2 save
```

**Configure Nginx reverse proxy:**
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/tm-backend
```

Paste the backend Nginx config (see `/nginx-configs/backend-nginx.conf`):

```bash
sudo ln -s /etc/nginx/sites-available/tm-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

> All above steps repeated identically on **TM-Backend-2**.

---

### Phase 5 — Frontend Configuration (TM-Frontend-1 and TM-Frontend-2)

**SSH into frontend instance:**
```bash
ssh -i ~/Downloads/travelmemory-key.pem ubuntu@<FRONTEND-EC2-PUBLIC-IP>
```

**Install dependencies (same as backend):**
```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs git nginx
sudo systemctl start nginx && sudo systemctl enable nginx
```

**Clone and update the backend URL:**
```bash
cd ~
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
nano ~/TravelMemory/frontend/src/url.js
```

Updated content:
```javascript
export const baseURL = "https://api.draxil.site"
```

**Install, build and deploy:**
```bash
cd ~/TravelMemory/frontend
npm install
npm run build
sudo cp -r build/* /var/www/html/
```

**Configure Nginx for React SPA:**
```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/tm-frontend
```

Paste the frontend Nginx config (see `/nginx-configs/frontend-nginx.conf`):

```bash
sudo ln -s /etc/nginx/sites-available/tm-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

> All above steps repeated identically on **TM-Frontend-2**.

---

### Phase 6 — AWS Load Balancers

**Create TM-Backend-TG (Target Group):**

Navigate to: EC2 → Target Groups → Create target group

```
Name:              TM-Backend-TG
Target type:       Instances
Protocol / Port:   HTTP / 80
Health check path: /
Targets:           TM-Backend-1, TM-Backend-2
```

**Create TM-Backend-ALB (Application Load Balancer):**

Navigate to: EC2 → Load Balancers → Create → Application Load Balancer

```
Name:       TM-Backend-ALB
Scheme:     Internet-facing
AZs:        All available (ap-south-1a, 1b, 1c)
Security:   TM-Backend-SG
Listener:   HTTP:80 → TM-Backend-TG
```

**Backend ALB DNS name:**
```
TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com
```

**Create TM-Frontend-TG and TM-Frontend-ALB** using the same process:

```
Frontend TG:  TM-Frontend-TG  (targets: TM-Frontend-1, TM-Frontend-2)
Frontend ALB: TM-Frontend-ALB → forwards to TM-Frontend-TG
```

**Frontend ALB DNS name:**
```
TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com
```

**Both target groups showing Healthy:**

---

### Phase 7 — Cloudflare Domain Setup

Domain purchased: **draxil.site** via Namecheap

**Added domain to Cloudflare → Updated nameservers at Namecheap:**

**Created 3 DNS records:**

| Type | Name | Value |
|------|------|-------|
| A | @ | TM-Frontend-1 Public IP |
| CNAME | www | TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com |
| CNAME | api | TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com |

**SSL Configuration — set to Flexible:**

> **Note:** Initially set to "Full" SSL mode which caused **Error 521** — Cloudflare
> was trying to connect to EC2 on port 443 (HTTPS) but Nginx only listens on port 80.
> Fixed by switching to **Flexible** mode (Cloudflare handles HTTPS externally,
> connects to EC2 internally via HTTP on port 80).

Enabled:
- Always Use HTTPS ✅
- Automatic HTTPS Rewrites ✅

---

### Phase 8 — Final Testing Results

| Test | URL Tested | Result |
|------|-----------|--------|
| Root domain | http://draxil.site | ✅ App loads |
| www HTTPS | https://www.draxil.site | ✅ App loads with 🔒 padlock |
| HTTP → HTTPS redirect | http://www.draxil.site | ✅ Auto-redirected to HTTPS |
| API endpoint | https://api.draxil.site | ✅ Backend responds |
| Backend load balancer | AWS console | ✅ Both targets Healthy |
| Frontend load balancer | AWS console | ✅ Both targets Healthy |
| End-to-end | Add travel memory | ✅ Saves and displays |

---

## ⚙️ Nginx Configurations

### Backend (Reverse Proxy)

See full file: [`nginx-configs/backend-nginx.conf`](nginx-configs/backend-nginx.conf)

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Frontend (React SPA)

See full file: [`nginx-configs/frontend-nginx.conf`](nginx-configs/frontend-nginx.conf)

```nginx
server {
    listen 80;
    server_name _;
    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, no-transform";
    }
}
```

---

## 🐛 Troubleshooting

### Error 521 — Web Server Down
**Root cause:** Cloudflare SSL set to "Full" → tries HTTPS on port 443 → EC2 Nginx only listens on port 80 → connection refused.

**Fix:** Cloudflare → SSL/TLS → Change from "Full" to **"Flexible"**

### PM2 App Shows "Errored"
```bash
pm2 logs tm-backend    # Read the error
cat .env               # Check MongoDB URI is correct
pm2 restart tm-backend # Restart after fixing
```

### Target Group Shows "Unhealthy"
```bash
sudo systemctl status nginx    # Is Nginx running?
pm2 status                     # Is Node.js app running?
curl http://localhost/         # Test locally
sudo systemctl restart nginx   # Restart if needed
```

### React App — API Calls Failing
```bash
cat ~/TravelMemory/frontend/src/url.js
# Must show: export const baseURL = "https://api.draxil.site"
# If wrong → fix the URL → rebuild → redeploy
cd ~/TravelMemory/frontend
npm run build
sudo cp -r build/* /var/www/html/
```

### SSH "Permission Denied"
```bash
# Make sure you have the right username (ubuntu for Ubuntu AMIs)
# Make sure you point to the correct .pem file
ssh -i ~/Downloads/travelmemory-key.pem ubuntu@YOUR-EC2-IP
```

---

## 📁 Repository Structure

```
TravelMemory-AWS-Deployment/
│
├── README.md                          ← Complete deployment documentation
│
├── architecture/
│   ├── TravelMemory-AWS-Architecture.png    ← Architecture diagram (PNG)
│   └── TravelMemory-AWS-Architecture.drawio ← Editable draw.io file
│
├── nginx-configs/
│   ├── backend-nginx.conf             ← Nginx reverse proxy config
│   └── frontend-nginx.conf            ← Nginx React SPA config
│
├── docs/
│   └── env-sample.txt                 ← .env file template (no secrets)
│
└── screenshots/                       ← 75 deployment screenshots
    ├── 01-aws-console-region.png
    ├── 02-key-pair-created.png
    └── ... (all 75 screenshots)
```

---

## 📚 References

- [TravelMemory Source Code](https://github.com/UnpredictablePrashant/TravelMemory)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [MongoDB Atlas Docs](https://www.mongodb.com/docs/atlas/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Cloudflare DNS Docs](https://developers.cloudflare.com/dns/)

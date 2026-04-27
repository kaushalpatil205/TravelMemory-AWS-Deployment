import re
import urllib.parse

# Mapping of old substring to new accurate file name
# We can just match the descriptive part of the old filename to the new one.
mapping = {
    "02-key-pair-travelmemory-key-created.png": "", # No image
    "03-TM-Backend-SG-inbound-rules.png": "1- Backend Security Group.png",
    "04-TM-Frontend-SG-inbound-rules.png": "2- Frontend Security Group.png",
    "06-mongodb-cluster-created.png": "3 - MongoDB user.png",
    "08-mongodb-network-access-allow-all.png": "4 - IP Access list.png",
    "10-all-4-ec2-instances-running.png": "6  - Backend Instances.png",
    "11-ec2-instances-public-ips-noted.png": "61 - Both instance active .png",
    "12-ssh-into-tm-backend-1.png": "9 - Accessing Backend Instance 1 .png",
    "13-nodejs-18-version-verified.png": "12 - NodeJS installed .png",
    "14-nginx-active-running-backend1.png": "13 - Nginx Server Started.png",
    "17-npm-install-backend-complete.png": "16 - Installing NPM  in Backend instance 1.png",
    "18-env-file-created-backend1.png": "17 - Connecting Database to Backend Instance one.png",
    "19-backend-server-started-mongodb-connected.png": " 19 - Backend Server Started.png",
    "20-pm2-status-online-backend1.png": "20.1 - PM2 Online.png",
    "22-nginx-config-test-ok-backend1.png": "23 -nginx-config-test-ok-backend1.png",
    "58-url-js-updated-api-draxil-site-frontend1.png": "36 -url-js-updated-backend-alb-dns-frontend1.png",
    "34-npm-build-success-frontend1.png": "38 - npm-build-success-frontend1.png",
    "37-travelmemory-app-browser-frontend1-ip.png": "41 - travelmemory-app-browser-frontend1-ip.png",
    "41-tm-backend-tg-created-both-instances.png": "30 - BACKEND target groups.png",
    "43-tm-backend-alb-active-status.png": "32 - Backend load balancer.png",
    "45-tm-frontend-alb-active-status.png": "45 Frontend ALB.png",
    "66-tm-backend-tg-both-targets-healthy.png": "68 T7 TG Backend Health.png",
    "67-tm-frontend-tg-both-targets-healthy.png": "67 T6 - TG frontend health.png",
    "50-namecheap-nameservers-updated-cloudflare.png": "48 - namecheap-nameservers-updated-cloudflare.png",
    "54-cloudflare-all-3-dns-records-together.png": "53 - Check cloudflare domain is active cloudflare-all-3-dns-records-together.png",
    "55-cloudflare-ssl-flexible-mode-selected.png": "54 -cloudflare-ssl-flexible-mode-selected.png",
    "72-error-521-before-fix.png": "",
    "73-ssl-changed-to-flexible-fix.png": "",
    "63-app-loading-https-www-draxil-site-padlock.png": "62 Test 1 Final Website from Frontend - Test www with HTTPS CNAME RECORD.png",
    "70-travel-memory-added-successfully.png": "65 T4 - Database is getting added in Database mongodb.png",
}

readme_text = """# 🌍 TravelMemory — MERN Stack AWS EC2 Deployment

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

All deployment screenshots are stored in the `/screenshots` folder documenting every step. See `DEPLOYMENT_DOCS.md` for a full step-by-step screenshot walkthrough.

---

## 📋 Step-by-Step Deployment

### Phase 1 — AWS Initial Setup

**1A. Create Key Pair**

Navigate to: EC2 → Network & Security → Key Pairs → Create key pair

![Key Pair Created](screenshots/02-key-pair-travelmemory-key-created.png)

```
Name:   travelmemory-key
Type:   RSA
Format: .pem
```

The `.pem` file downloads automatically. It is the only way to SSH into your servers.

**1B. Create Backend Security Group (TM-Backend-SG)**

Navigate to: EC2 → Security Groups → Create security group

![Backend SG](screenshots/03-TM-Backend-SG-inbound-rules.png)

**1C. Create Frontend Security Group (TM-Frontend-SG)**

![Frontend SG](screenshots/04-TM-Frontend-SG-inbound-rules.png)

---

### Phase 2 — MongoDB Atlas Database

![MongoDB Cluster](screenshots/06-mongodb-cluster-created.png)

1. Created free M0 cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Cluster: `TravelMemoryCluster`, Region: `ap-south-1`
3. Database user: `tmuser` with Atlas admin role
4. Network Access: `0.0.0.0/0` — allows all IP addresses

![Network Access](screenshots/08-mongodb-network-access-allow-all.png)

Connection string format:
```
mongodb+srv://tmuser:<password>@travelmemorycluster.xxxxx.mongodb.net/travelmemory?retryWrites=true&w=majority
```

---

### Phase 3 — Launch 4 EC2 Instances

![All 4 Instances](screenshots/10-all-4-ec2-instances-running.png)

Each instance created with:
- AMI: **Ubuntu Server 22.04 LTS**
- Type: **t2.micro** (free tier)
- Key pair: **travelmemory-key**
- Storage: 8 GB gp2

![Instances With IPs](screenshots/11-ec2-instances-public-ips-noted.png)

---

### Phase 4 — Backend Configuration (TM-Backend-1 and TM-Backend-2)

**SSH into the instance:**
```bash
ssh -i ~/Downloads/travelmemory-key.pem ubuntu@<BACKEND-EC2-PUBLIC-IP>
```

![SSH Connected](screenshots/12-ssh-into-tm-backend-1.png)

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

![Node.js Version](screenshots/13-nodejs-18-version-verified.png)
![Nginx Running](screenshots/14-nginx-active-running-backend1.png)

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

![npm install](screenshots/17-npm-install-backend-complete.png)

**Create the .env file:**
```bash
nano .env
```

Contents:
```
PORT=3000
MONGO_URI=mongodb+srv://tmuser:TravelMemory@2024@travelmemorycluster.xxxxx.mongodb.net/travelmemory?retryWrites=true&w=majority
```

![.env File](screenshots/18-env-file-created-backend1.png)

**Test the server runs:**
```bash
node index.js
# Should show: Server running on port 3000 + MongoDB connected
```

![Server Started](screenshots/19-backend-server-started-mongodb-connected.png)

**Start with PM2:**
```bash
sudo npm install -g pm2
pm2 start index.js --name "tm-backend"
pm2 startup
# Run the command PM2 outputs above
pm2 save
```

![PM2 Online](screenshots/20-pm2-status-online-backend1.png)

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

![Nginx Test OK](screenshots/22-nginx-config-test-ok-backend1.png)

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

![URL.js Updated](screenshots/58-url-js-updated-api-draxil-site-frontend1.png)

**Install, build and deploy:**
```bash
cd ~/TravelMemory/frontend
npm install
npm run build
sudo cp -r build/* /var/www/html/
```

![Build Success](screenshots/34-npm-build-success-frontend1.png)

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

![App in Browser](screenshots/37-travelmemory-app-browser-frontend1-ip.png)

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

![Backend TG](screenshots/41-tm-backend-tg-created-both-instances.png)

**Create TM-Backend-ALB (Application Load Balancer):**

Navigate to: EC2 → Load Balancers → Create → Application Load Balancer

```
Name:       TM-Backend-ALB
Scheme:     Internet-facing
AZs:        All available (ap-south-1a, 1b, 1c)
Security:   TM-Backend-SG
Listener:   HTTP:80 → TM-Backend-TG
```

![Backend ALB Active](screenshots/43-tm-backend-alb-active-status.png)

**Backend ALB DNS name:**
```
TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com
```

**Create TM-Frontend-TG and TM-Frontend-ALB** using the same process:

```
Frontend TG:  TM-Frontend-TG  (targets: TM-Frontend-1, TM-Frontend-2)
Frontend ALB: TM-Frontend-ALB → forwards to TM-Frontend-TG
```

![Frontend ALB Active](screenshots/45-tm-frontend-alb-active-status.png)

**Frontend ALB DNS name:**
```
TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com
```

**Both target groups showing Healthy:**

![Backend Targets Healthy](screenshots/66-tm-backend-tg-both-targets-healthy.png)
![Frontend Targets Healthy](screenshots/67-tm-frontend-tg-both-targets-healthy.png)

---

### Phase 7 — Cloudflare Domain Setup

Domain purchased: **draxil.site** via Namecheap

**Added domain to Cloudflare → Updated nameservers at Namecheap:**

![Namecheap Nameservers Updated](screenshots/50-namecheap-nameservers-updated-cloudflare.png)

**Created 3 DNS records:**

![All DNS Records](screenshots/54-cloudflare-all-3-dns-records-together.png)

| Type | Name | Value |
|------|------|-------|
| A | @ | TM-Frontend-1 Public IP |
| CNAME | www | TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com |
| CNAME | api | TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com |

**SSL Configuration — set to Flexible:**

![SSL Flexible](screenshots/55-cloudflare-ssl-flexible-mode-selected.png)

> **Note:** Initially set to "Full" SSL mode which caused **Error 521** — Cloudflare
> was trying to connect to EC2 on port 443 (HTTPS) but Nginx only listens on port 80.
> Fixed by switching to **Flexible** mode (Cloudflare handles HTTPS externally,
> connects to EC2 internally via HTTP on port 80).

![Error 521](screenshots/72-error-521-before-fix.png)
![Fixed with Flexible](screenshots/73-ssl-changed-to-flexible-fix.png)

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

![App with HTTPS Padlock](screenshots/63-app-loading-https-www-draxil-site-padlock.png)
![Memory Added](screenshots/70-travel-memory-added-successfully.png)

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
│   └── preview.webp                         ← Editable draw.io file image
│
├── nginx-configs/
│   ├── backend-nginx.conf             ← Nginx reverse proxy config
│   └── frontend-nginx.conf            ← Nginx React SPA config
│
├── docs/
│   └── env-sample.txt                 ← .env file template (no secrets)
│
└── screenshots/                       ← 75 deployment screenshots
    ├── 1- Backend Security Group.png
    └── ... (all deployment screenshots)
```

---

## 📚 References

- [TravelMemory Source Code](https://github.com/UnpredictablePrashant/TravelMemory)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [MongoDB Atlas Docs](https://www.mongodb.com/docs/atlas/)
- [Nginx Docs](https://nginx.org/en/docs/)
- [PM2 Documentation](https://pm2.keymetrics.io/docs/)
- [Cloudflare DNS Docs](https://developers.cloudflare.com/dns/)
"""

# Replace all old links with new mapped ones, removing ones that don't map
lines = readme_text.split('\n')
new_lines = []

for line in lines:
    if line.startswith('![') and '](' in line:
        start_idx = line.find('](') + 2
        end_idx = line.find(')', start_idx)
        img_path = line[start_idx:end_idx]
        
        # Only process screenshots
        if img_path.startswith('screenshots/'):
            filename = img_path.replace('screenshots/', '')
            if filename in mapping:
                new_filename = mapping[filename]
                if new_filename == "":
                    # Skip this image line completely
                    continue
                else:
                    new_path = "screenshots/" + urllib.parse.quote(new_filename)
                    line = line[:start_idx] + new_path + line[end_idx:]
    
    new_lines.append(line)

with open("README.md", "w") as f:
    f.write('\n'.join(new_lines))


import urllib.parse

def encode_path(filename):
    return "screenshots/" + urllib.parse.quote(filename)

deployment_content = f"""# Deployment Guide: Travel Memory Application

This document provides a step-by-step walkthrough to deploy the Travel Memory MERN application on AWS EC2, configured with NGINX reverse proxies, Application Load Balancing, and a custom domain via Cloudflare.

## Prerequisites
- An AWS Account.
- A Cloudflare Account with a registered custom domain.
- A MongoDB Atlas cluster (with a connection string).

---

## Step 1: Launch EC2 Instances

For scaling, we will launch multiple EC2 instances. In a basic setup, you can have 2 Frontend instances and 2 Backend instances.

1. Navigate to the **EC2 Dashboard** in your AWS Management Console.
![EC2 Dashboard]({encode_path('6  - Backend Instances.png')})
2. Click **Launch Instance**. Choose an **Ubuntu Server 22.04 LTS** (or 24.04 LTS) AMI.
![Ubuntu Server]({encode_path('10 - Backend Instance setup 1 .png')})
3. Configure Security Group:
   - **SSH (Port 22)**: Allow from your IP.
   - **HTTP (Port 80)**: Allow from anywhere.
   - **HTTPS (Port 443)**: Allow from anywhere.
   - **Custom TCP (Port 3000)**: Allow from your ALB or anywhere.
   ![Backend Security Group]({encode_path('1- Backend Security Group.png')})
   ![Frontend Security Group]({encode_path('2- Frontend Security Group.png')})
4. Launch and download the PEM key pair. Repeat this to create multiple instances for high availability.
![Multiple Instances Running]({encode_path('61 - Both instance active .png')})

---

## Step 2: Environment Setup connect to EC2

Click on instance and click on connect button.
![Connect to instance]({encode_path('9 - Accessing Backend Instance 1 .png')})

Install the required dependencies (Node.js, Git, NGINX) on all instances:
```bash
sudo apt update
sudo apt install -y curl git nginx
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```
![Installing Node.js]({encode_path('11 - Installing NodeJs.png')})
![Node.js Installed]({encode_path('12 - NodeJS installed .png')})

---

## Step 3: Backend Configuration & Deployment

### 1. Clone the repository in both backend instances
```bash
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/backend
```
![Cloned the repository]({encode_path('15 - Cloning Git Repo in Backend Instance 1 .png')})

### 2. Configure `.env`
Create a `.env` file in the `backend` directory:
```bash
nano .env
```
Connect to MongoDB Atlas and copy the connection string.
![MongoDB User]({encode_path('3 - MongoDB user.png')})
![MongoDB IP Access]({encode_path('4 - IP Access list.png')})
![MongoDB Connection String]({encode_path('5 - MONGODB connection string.png')})

```env
PORT=3000
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/travelmemory?retryWrites=true&w=majority
```
![Added connection string to env]({encode_path('17 - Connecting Database to Backend Instance one.png')})

### 3. Install Dependencies & PM2
```bash
npm install
sudo npm install -g pm2
pm2 start index.js --name "travel-backend"
pm2 save
pm2 startup
```
![NPM Install]({encode_path('16 - Installing NPM  in Backend instance 1.png')})
![Installing PM2]({encode_path('18 - Installing PM2.png')})
![Backend Server Started]({encode_path(' 19 - Backend Server Started.png')})
![PM2 Save]({encode_path('22 PM2 Save.png')})

### 4. Setup Nginx Reverse Proxy for Backend
Create an Nginx configuration file (`/etc/nginx/sites-available/backend`):
```bash
sudo nano /etc/nginx/sites-available/backend
```
setup reverse proxy for backend
```nginx
server {{
    listen 80;
    server_name _;

    location / {{
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}
}}
```
![Setup Reverse proxy]({encode_path('24- nginx-reverse-proxy-config-backend1.png')})

Link and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```
![Link and restart Nginx]({encode_path('23 -nginx-config-test-ok-backend1.png')})

---

## Step 4: Frontend Configuration & Deployment

### 1. Update Frontend `url.js`
In the frontend instance, clone the project and navigate to the `frontend` folder:
```bash
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/frontend
```
![Clone Frontend Repo]({encode_path('33 -FRONTEND SETUP ON TM-Frontend-1.png')})

Set your environment variable for production:
```bash
nano .env
```
Inside env file add the following:
```bash
REACT_APP_BACKEND_URL=http://<YOUR_BACKEND_IP>
```
![Update url.js]({encode_path('36 -url-js-updated-backend-alb-dns-frontend1.png')})

### 2. Build the Application
```bash
npm install
npm run build
```
![NPM Install Frontend]({encode_path('37 - npm-install-frontend1-complete.png')})
![Build Frontend]({encode_path('38 - npm-build-success-frontend1.png')})

### 3. Serve Frontend via Nginx
Copy the built files to the NGINX web root:
```bash
sudo cp -r build/* /var/www/html/
```
![Copy build files]({encode_path('39 - files-copied-to-var-www-html-frontend1.png')})

Update NGINX to serve the React application (`/etc/nginx/sites-available/default`):
```bash
sudo nano /etc/nginx/sites-available/default
```
```nginx
server {{
    listen 80;

    root /var/www/html;
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ /index.html;
    }}
}}
```
Restart Nginx: `sudo systemctl restart nginx`
![Frontend Config OK]({encode_path('40 - nginx-frontend-config-test-ok..png')})

Now copy the frontend ip address and paste it in your browser.
![Frontend App Live]({encode_path('41 - travelmemory-app-browser-frontend1-ip.png')})

---

## Step 5: Application Load Balancer Configuration

Part A : Create Target Groups
1. Navigate to Target Groups and click Create target group.
2. Choose Instances, Name it `frontend-tg`, HTTP/80.
3. Select the Frontend EC2 instances and Create target group.
![Frontend Target Group]({encode_path('44 Frontend TG.png')})
4. Repeat for the Backend instances to create `backend-tg`.
![Backend Target Group]({encode_path('30 - BACKEND target groups.png')})

Part B : Create Load Balancer
1. Go to Load Balancers -> Create Application Load Balancer.
2. Name it, scheme Internet-facing.
![Frontend ALB]({encode_path('45 Frontend ALB.png')})
![Backend ALB]({encode_path('32 - Backend load balancer.png')})

Part C : Route Testing
Test by sending traffic to the Load Balancer DNS names.
![Test ALB]({encode_path('46 - Testing using ALB.png')})

---

## Step 6: Domain Setup with Cloudflare

Part 1: Connect your new domain to Cloudflare
1. Log into your registrar (like Namecheap) and change nameservers to Cloudflare.
![Domain buy]({encode_path('47 Domain buy .png')})
![Nameservers]({encode_path('48 - namecheap-nameservers-updated-cloudflare.png')})
![Active Status]({encode_path('49 - Verification from cloudflare for site .png')})

Part 2: Add DNS Records
1. Add the CNAME Record for ALB.
![DNS A Record]({encode_path('50 -cloudflare-dns-A-record-root-domain.png')})
![DNS CNAME WWW]({encode_path('51- cloudflare-dns-CNAME-www-frontend-alb.png')})
![DNS CNAME API]({encode_path('52 - cloudflare-dns-CNAME-api-backend-alb.png')})
![All Records Together]({encode_path('53 - Check cloudflare domain is active cloudflare-all-3-dns-records-together.png')})

Part 3: SSL Configuration
Switch SSL mode to Flexible.
![SSL Flexible Mode]({encode_path('54 -cloudflare-ssl-flexible-mode-selected.png')})
Enable Always Use HTTPS and HTTPS Rewrites.
![Always Use HTTPS]({encode_path('55 - cloudflare-always-use-https-enabled.png')})
![HTTPS Rewrites]({encode_path('56 - cloudflare-automatic-https-rewrites-on.png')})

---

## Step 7: Final Tests and Health Checks

With instances connected to the Application Load balancer and routed through Cloudflare, the application is live and secured.

1. Website accessible via HTTPS CNAME
![Test 1]({encode_path('62 Test 1 Final Website from Frontend - Test www with HTTPS CNAME RECORD.png')})
2. HTTP successfully redirects to HTTPS
![Test 2]({encode_path('63 Test 2 Final Website - Test HTTP Redirects to HTTPS.png')})
3. Backend API reaches successfully
![Backend API]({encode_path('64 T3 Backend api .png')})
4. Database stores data
![Database Insert]({encode_path('65 T4 - Database is getting added in Database mongodb.png')})
5. SSL Certificate valid
![SSL Valid]({encode_path('66 T5-SSL Certificate Details.png')})

Target Group Health Validations:
![TG Frontend Health]({encode_path('67 T6 - TG frontend health.png')})
![TG Backend Health]({encode_path('68 T7 TG Backend Health.png')})
![ALB Frontend Health]({encode_path('69 T9 Test Load Balancer Health Frontend.png')})
![ALB Backend Health]({encode_path('70 T10 Test Load Balancer Health Backend.png')})

"""

with open("DEPLOYMENT_DOCS.md", "w") as f:
    f.write(deployment_content)

readme_content = f"""# 🌍 TravelMemory — MERN Stack AWS EC2 Deployment

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

![TravelMemory AWS Architecture](architecture/TravelMemory-AWS-Architecture.png)

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

**1B. Create Backend Security Group (TM-Backend-SG)**
![Backend SG]({encode_path('1- Backend Security Group.png')})

**1C. Create Frontend Security Group (TM-Frontend-SG)**
![Frontend SG]({encode_path('2- Frontend Security Group.png')})

---

### Phase 2 — MongoDB Atlas Database

![MongoDB Cluster]({encode_path('3 - MongoDB user.png')})

1. Created free M0 cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Network Access: `0.0.0.0/0` — allows all IP addresses

![Network Access]({encode_path('4 - IP Access list.png')})

Connection string:
![Connection string]({encode_path('5 - MONGODB connection string.png')})

---

### Phase 3 — Launch 4 EC2 Instances

![All 4 Instances]({encode_path('6  - Backend Instances.png')})

Each instance created with:
- AMI: **Ubuntu Server 22.04 LTS**
- Type: **t2.micro** (free tier)

---

### Phase 4 — Backend Configuration (TM-Backend-1 and TM-Backend-2)

**SSH into the instance:**
![SSH Connected]({encode_path('9 - Accessing Backend Instance 1 .png')})

**Install all dependencies:**
![Node.js Installed]({encode_path('12 - NodeJS installed .png')})

**Clone the repository:**
![Repo Clone]({encode_path('15 - Cloning Git Repo in Backend Instance 1 .png')})

**Create the .env file:**
![.env File]({encode_path('17 - Connecting Database to Backend Instance one.png')})

**Test the server runs:**
![Server Started]({encode_path(' 19 - Backend Server Started.png')})

**Start with PM2:**
![PM2 Online]({encode_path('20.1 - PM2 Online.png')})

**Configure Nginx reverse proxy:**
![Nginx Test OK]({encode_path('23 -nginx-config-test-ok-backend1.png')})

---

### Phase 5 — Frontend Configuration (TM-Frontend-1 and TM-Frontend-2)

**Install dependencies & clone:**
![Clone Frontend]({encode_path('33 -FRONTEND SETUP ON TM-Frontend-1.png')})

Updated URL content:
![URL.js Updated]({encode_path('36 -url-js-updated-backend-alb-dns-frontend1.png')})

**Install, build and deploy:**
![Build Success]({encode_path('38 - npm-build-success-frontend1.png')})

**Configure Nginx for React SPA:**
![App in Browser]({encode_path('41 - travelmemory-app-browser-frontend1-ip.png')})

---

### Phase 6 — AWS Load Balancers

**Create Target Groups:**
![Backend TG]({encode_path('30 - BACKEND target groups.png')})
![Frontend TG]({encode_path('44 Frontend TG.png')})

**Create Application Load Balancers:**
![Frontend ALB Active]({encode_path('45 Frontend ALB.png')})
![Backend ALB Active]({encode_path('32 - Backend load balancer.png')})

---

### Phase 7 — Cloudflare Domain Setup

Domain purchased: **draxil.site** via Namecheap

**Added domain to Cloudflare → Updated nameservers at Namecheap:**
![Namecheap Nameservers Updated]({encode_path('48 - namecheap-nameservers-updated-cloudflare.png')})

**Created 3 DNS records:**
![All DNS Records]({encode_path('53 - Check cloudflare domain is active cloudflare-all-3-dns-records-together.png')})

**SSL Configuration — set to Flexible:**
![SSL Flexible]({encode_path('54 -cloudflare-ssl-flexible-mode-selected.png')})

---

### Phase 8 — Final Testing Results

| Test | URL Tested | Result |
|------|-----------|--------|
| Root domain | http://draxil.site | ✅ App loads |
| www HTTPS | https://www.draxil.site | ✅ App loads with 🔒 padlock |
| HTTP → HTTPS redirect | http://www.draxil.site | ✅ Auto-redirected to HTTPS |
| API endpoint | https://api.draxil.site | ✅ Backend responds |

![App with HTTPS Padlock]({encode_path('62 Test 1 Final Website from Frontend - Test www with HTTPS CNAME RECORD.png')})
![Memory Added]({encode_path('65 T4 - Database is getting added in Database mongodb.png')})

---

## ⚙️ Nginx Configurations

### Backend (Reverse Proxy)

See full file: [`nginx-configs/backend-nginx.conf`](nginx-configs/backend-nginx.conf)

### Frontend (React SPA)

See full file: [`nginx-configs/frontend-nginx.conf`](nginx-configs/frontend-nginx.conf)

---

## 🐛 Troubleshooting

### Error 521 — Web Server Down
**Root cause:** Cloudflare SSL set to "Full" → tries HTTPS on port 443 → EC2 Nginx only listens on port 80 → connection refused.

**Fix:** Cloudflare → SSL/TLS → Change from "Full" to **"Flexible"**

---

## 📁 Repository Structure

```
TravelMemory-AWS-Deployment/
│
├── README.md                          ← Complete deployment documentation
├── DEPLOYMENT_DOCS.md                 ← Step by step deployment with images
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

with open("README.md", "w") as f:
    f.write(readme_content)


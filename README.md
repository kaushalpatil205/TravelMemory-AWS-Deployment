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
![Backend SG](screenshots/1-%20Backend%20Security%20Group.png)

**1C. Create Frontend Security Group (TM-Frontend-SG)**
![Frontend SG](screenshots/2-%20Frontend%20Security%20Group.png)

---

### Phase 2 — MongoDB Atlas Database

![MongoDB Cluster](screenshots/3%20-%20MongoDB%20user.png)

1. Created free M0 cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Network Access: `0.0.0.0/0` — allows all IP addresses

![Network Access](screenshots/4%20-%20IP%20Access%20list.png)

Connection string:
![Connection string](screenshots/5%20-%20MONGODB%20connection%20string.png)

---

### Phase 3 — Launch 4 EC2 Instances

![All 4 Instances](screenshots/6%20%20-%20Backend%20Instances.png)

Each instance created with:
- AMI: **Ubuntu Server 22.04 LTS**
- Type: **t2.micro** (free tier)

---

### Phase 4 — Backend Configuration (TM-Backend-1 and TM-Backend-2)

**SSH into the instance:**
![SSH Connected](screenshots/9%20-%20Accessing%20Backend%20Instance%201%20.png)

**Install all dependencies:**
![Node.js Installed](screenshots/12%20-%20NodeJS%20installed%20.png)

**Clone the repository:**
![Repo Clone](screenshots/15%20-%20Cloning%20Git%20Repo%20in%20Backend%20Instance%201%20.png)

**Create the .env file:**
![.env File](screenshots/17%20-%20Connecting%20Database%20to%20Backend%20Instance%20one.png)

**Test the server runs:**
![Server Started](screenshots/%2019%20-%20Backend%20Server%20Started.png)

**Start with PM2:**
![PM2 Online](screenshots/20.1%20-%20PM2%20Online.png)

**Configure Nginx reverse proxy:**
![Nginx Test OK](screenshots/23%20-nginx-config-test-ok-backend1.png)

---

### Phase 5 — Frontend Configuration (TM-Frontend-1 and TM-Frontend-2)

**Install dependencies & clone:**
![Clone Frontend](screenshots/33%20-FRONTEND%20SETUP%20ON%20TM-Frontend-1.png)

Updated URL content:
![URL.js Updated](screenshots/36%20-url-js-updated-backend-alb-dns-frontend1.png)

**Install, build and deploy:**
![Build Success](screenshots/38%20-%20npm-build-success-frontend1.png)

**Configure Nginx for React SPA:**
![App in Browser](screenshots/41%20-%20travelmemory-app-browser-frontend1-ip.png)

---

### Phase 6 — AWS Load Balancers

**Create Target Groups:**
![Backend TG](screenshots/30%20-%20BACKEND%20target%20groups.png)
![Frontend TG](screenshots/44%20Frontend%20TG.png)

**Create Application Load Balancers:**
![Frontend ALB Active](screenshots/45%20Frontend%20ALB.png)
![Backend ALB Active](screenshots/32%20-%20Backend%20load%20balancer.png)

---

### Phase 7 — Cloudflare Domain Setup

Domain purchased: **draxil.site** via Namecheap

**Added domain to Cloudflare → Updated nameservers at Namecheap:**
![Namecheap Nameservers Updated](screenshots/48%20-%20namecheap-nameservers-updated-cloudflare.png)

**Created 3 DNS records:**
![All DNS Records](screenshots/53%20-%20Check%20cloudflare%20domain%20is%20active%20cloudflare-all-3-dns-records-together.png)

**SSL Configuration — set to Flexible:**
![SSL Flexible](screenshots/54%20-cloudflare-ssl-flexible-mode-selected.png)

---

### Phase 8 — Final Testing Results

| Test | URL Tested | Result |
|------|-----------|--------|
| Root domain | http://draxil.site | ✅ App loads |
| www HTTPS | https://www.draxil.site | ✅ App loads with 🔒 padlock |
| HTTP → HTTPS redirect | http://www.draxil.site | ✅ Auto-redirected to HTTPS |
| API endpoint | https://api.draxil.site | ✅ Backend responds |

![App with HTTPS Padlock](screenshots/62%20Test%201%20Final%20Website%20from%20Frontend%20-%20Test%20www%20with%20HTTPS%20CNAME%20RECORD.png)
![Memory Added](screenshots/65%20T4%20-%20Database%20is%20getting%20added%20in%20Database%20mongodb.png)

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

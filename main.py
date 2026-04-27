#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 12:40:40 2026

@author: Vraj
"""

# Deployment Guide: TravelMemory Application

This document provides a complete step-by-step walkthrough to deploy the TravelMemory MERN application on AWS EC2, configured with Nginx reverse proxies, Application Load Balancing (ALB), and a custom domain via Cloudflare.

**Live Application:** https://www.draxil.site  
**Backend API:** https://api.draxil.site  
**GitHub Repository:** https://github.com/kaushalpatil205/TravelMemory-AWS-Deployment

---

## Prerequisites

- An AWS Account (free tier)
- A Cloudflare Account with a registered custom domain (`draxil.site`)
- A MongoDB Atlas cluster (M0 Free tier)
- A key pair `.pem` file for SSH access

---

## Architecture Overview

![Deployment Architecture](architecture/architecture-diagram.png)

The deployment consists of:
- **2 Frontend EC2 instances** (TM-Frontend-1, TM-Frontend-2) — serve the React build via Nginx
- **2 Backend EC2 instances** (TM-Backend-1, TM-Backend-2) — run Node.js API via PM2 + Nginx reverse proxy
- **2 AWS Application Load Balancers** — TM-Frontend-ALB and TM-Backend-ALB
- **MongoDB Atlas** — cloud-hosted database (TravelMemoryCluster)
- **Cloudflare** — DNS management, SSL termination, and CDN

---

## Step 1: Launch EC2 Instances

We launch 4 EC2 instances — 2 for the frontend, 2 for the backend — for high availability and load balancing.

### 1A. Open EC2 Dashboard

1. Log into the **AWS Management Console**
2. Search for **EC2** in the top search bar and click it
3. You are now on the EC2 Dashboard

![EC2 Dashboard]('/Users/Vraj/Desktop/screenshots/7 - Backend Instance running .png' and '/Users/Vraj/Desktop/screenshots/8 - Frontend Instance running .png' )

### 1B. Launch an Instance

Click the orange **Launch instance** button.

Fill in the following:

| Setting | Value |
|---------|-------|
| Name | `TM-Backend-1` (then repeat for TM-Backend-2, TM-Frontend-1, TM-Frontend-2) |
| AMI | Ubuntu Server 22.04 LTS (HVM), SSD Volume Type |
| Architecture | 64-bit (x86) |
| Instance type | `t2.micro` (Free Tier eligible) |
| Key pair | `travelmemory-key` (create once, reuse for all 4) |
| Storage | 8 GiB gp2 |

![Choose Ubuntu Server 22.04 LTS]('/Users/Vraj/Desktop/screenshots/1- Backend Security Group.png')

### 1C. Configure Security Groups

Create **two security groups**:

**TM-Backend-SG** (for both backend instances):

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | My IP |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 |

**TM-Frontend-SG** (for both frontend instances):

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| SSH | TCP | 22 | My IP |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |

![Security Group configuration]('/Users/Vraj/Desktop/screenshots/1- Backend Security Group.png'
![Frontend Security Group]('/Users/Vraj/Desktop/screenshots/2- Frontend Security Group.png')

### 1D. Launch All 4 Instances

Repeat the launch process for each instance. Use `TM-Backend-SG` for the two backend instances and `TM-Frontend-SG` for the two frontend instances.

After launching, all 4 instances should show **Running** state:

![All 4 EC2 Instances Running](('/Users/Vraj/Desktop/screenshots/7 - Backend Instance running .png' and '/Users/Vraj/Desktop/screenshots/8 - Frontend Instance running .png' ))


---

## Step 2: Connect to EC2 and Install Dependencies

Perform these steps on **all 4 instances** (both backend and frontend).

### 2A. SSH Into the Instance

Open your terminal and run:

```bash
ssh -i ~/Downloads/travelmemory-key.pem ubuntu@<YOUR-EC2-PUBLIC-IP>
```

When prompted with "Are you sure you want to continue connecting?" — type `yes` and press Enter.

![SSH into Backend Instance]('/Users/Vraj/Desktop/screenshots/9 - Accessing Backend Instance 1 .png')

### 2B. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2C. Install Node.js 18 LTS

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify the installation:

```bash
node --version   # Should show v18.x.x
npm --version    # Should show 9.x.x
```

![Node.js version verified]('/Users/Vraj/Desktop/screenshots/10 - Backend Instance setup 1 .png' and '/Users/Vraj/Desktop/screenshots/11 - Installing NodeJs.png' and '/Users/Vraj/Desktop/screenshots/12 - NodeJS installed .png')

### 2D. Install Git and Nginx

```bash
sudo apt install -y git nginx
```

Start and enable Nginx so it runs automatically on reboot:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

![Nginx active and running]('/Users/Vraj/Desktop/screenshots/13 - Nginx Server Started.png' and '/Users/Vraj/Desktop/screenshots/14 - Nginx on browser.png')

---

## Step 3: Backend Configuration and Deployment

Perform **Steps 3A through 3E** on **both TM-Backend-1 and TM-Backend-2**.

### 3A. Clone the Repository

```bash
cd ~
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/backend
```

![Repository cloned on backend instance]('/Users/Vraj/Desktop/screenshots/15 - Cloning Git Repo in Backend Instance 1 .png')

### 3B. Configure MongoDB Atlas

Before creating the `.env` file, get your MongoDB Atlas connection string:

1. Log into [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Click your cluster (**TravelMemoryCluster**) → **Connect** → **Connect your application**
3. Choose **Node.js** driver, version **4.1 or later**
4. Copy the connection string

![MongoDB Atlas connection string]('/Users/Vraj/Desktop/screenshots/5 - MONGODB connection string.png')

### 3C. Create the `.env` File

```bash
nano .env
```

Add the following (replace with your actual MongoDB URI):

```env
PORT=3000
MONGO_URI=mongodb+srv://tmuser:TravelMemory@2024@travelmemorycluster.xxxxx.mongodb.net/travelmemory?retryWrites=true&w=majority
```



### 3D. Install Dependencies and Start with PM2

```bash
npm install
sudo npm install -g pm2
```

Test the server runs correctly:

```bash
node index.js
# Should show: Server running on port 3000
# And: Connected to MongoDB
```

Press `Ctrl+C` to stop the test. Then start with PM2:

```bash
pm2 start index.js --name "tm-backend"
pm2 status
```

![PM2 status showing tm-backend online]('/Users/Vraj/Desktop/screenshots/20.1 - PM2 Online.png')

Make PM2 start automatically on server reboot:

```bash
pm2 startup
# Copy and run the command PM2 outputs
pm2 save
```

![PM2 startup and save]('/Users/Vraj/Desktop/screenshots/21 -PM2 Startup .png' and '/Users/Vraj/Desktop/screenshots/22 PM2 Save.png')

### 3E. Configure Nginx as Reverse Proxy

Remove the default Nginx config and create a new one:

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/tm-backend
```

Add the following configuration:

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

Enable the config and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/tm-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

The `nginx -t` command must show:
```
nginx: the configuration file syntax is ok
nginx: configuration file test is successful
```

![Nginx config test successful on backend]('/Users/Vraj/Desktop/screenshots/23 -nginx-config-test-ok-backend1.png')

Test by opening `http://<BACKEND-EC2-IP>` in your browser — you should see an API response.

![Backend API response in browser]('/Users/Vraj/Desktop/screenshots/26 - backend-api-response-browser-backend instance 1-ip.png')

> Repeat all of Step 3 identically on **TM-Backend-2**.

![PM2 online on Backend-2]('/Users/Vraj/Desktop/screenshots/27-TM-Backend Instance-2 Online.png')

---

## Step 4: Frontend Configuration and Deployment

Perform **Steps 4A through 4E** on **both TM-Frontend-1 and TM-Frontend-2**.

### 4A. Clone the Repository

SSH into the frontend instance, then:

```bash
cd ~
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/frontend
```

![Repository cloned on frontend instance]('/Users/Vraj/Desktop/screenshots/35 nginx-active-running-frontend1 and git cloning in frontend.png')

### 4B. Update the Backend URL in `url.js`

The React app needs to know where to send API requests. Update the backend URL to point to your API subdomain (which will route through Cloudflare to the Backend ALB):

```bash
nano src/url.js
```

Change the content to:

```javascript
export const baseURL = "https://api.draxil.site"
```

> **Why this URL?** After Cloudflare and the Backend ALB are set up, `api.draxil.site` routes to your backend instances. The `https://` is provided by Cloudflare's SSL termination.

![url.js updated with api.draxil.site]('/Users/Vraj/Desktop/screenshots/36 -url-js-updated-backend-alb-dns-frontend1.png')

### 4C. Install Dependencies and Build

```bash
npm install
npm run build
```

The build process compiles React JSX into optimized static HTML/CSS/JavaScript files, outputting them to a `build/` folder.

![npm build success on Frontend-1]('/Users/Vraj/Desktop/screenshots/38 - npm-build-success-frontend1.png')

### 4D. Deploy Build Files to Nginx

Copy the built files to Nginx's web root directory:

```bash
sudo cp -r build/* /var/www/html/
```

### 4E. Configure Nginx for React SPA

Remove the default config and create a new one:

```bash
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/nginx/sites-available/tm-frontend
```

Add the following configuration:

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

> **Why `try_files $uri $uri/ /index.html`?** React uses client-side routing. Without this, refreshing the browser on any route like `/memories` returns a 404. This rule ensures Nginx always serves `index.html` and lets React Router handle the navigation.

Enable the config:

```bash
sudo ln -s /etc/nginx/sites-available/tm-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

![Nginx frontend config test successful]('/Users/Vraj/Desktop/screenshots/35 nginx-active-running-frontend1 and git cloning in frontend.png')

Open `http://<FRONTEND-EC2-IP>` in your browser — you should see the TravelMemory React application:

![TravelMemory app in browser via Frontend-1 IP]('/Users/Vraj/Desktop/screenshots/41 - travelmemory-app-browser-frontend1-ip.png')

> Repeat all of Step 4 identically on **TM-Frontend-2**.

![TravelMemory app via Frontend-2 IP]('/Users/Vraj/Desktop/screenshots/43 Frontend started for Frontend instance 2.png')

---

## Step 5: Application Load Balancer Configuration

### Part A: Create Target Groups

A **Target Group** is a list of EC2 instances that the Load Balancer distributes traffic to. It also performs health checks — if an instance fails a health check, the ALB stops sending it traffic.

#### Create Backend Target Group (TM-Backend-TG)

1. In EC2 Dashboard → left sidebar → **Target Groups** → **Create target group**

![Create target group button]('/Users/Vraj/Desktop/screenshots/30 - BACKEND target groups.png' and '/Users/Vraj/Desktop/screenshots/31 - backend target groups running.png')

2. Fill in:

| Field | Value |
|-------|-------|
| Target type | Instances |
| Target group name | `TM-Backend-TG` |
| Protocol | HTTP |
| Port | 80 |
| VPC | Default VPC |
| Health check path | `/` |

3. Click **Next** → Select **TM-Backend-1** and **TM-Backend-2** from the list → Click **Include as pending below** → Click **Create target group**

#### Create Frontend Target Group (TM-Frontend-TG)

Repeat the same steps with:
- Target group name: `TM-Frontend-TG`
- Select: **TM-Frontend-1** and **TM-Frontend-2**

![Both target groups created]('/Users/Vraj/Desktop/screenshots/44 Frontend TG.png')

---

### Part B: Create Application Load Balancers

#### Create Backend ALB (TM-Backend-ALB)

1. EC2 Dashboard → **Load Balancers** → **Create Load Balancer** → Choose **Application Load Balancer**

![Create Load Balancer]('/Users/Vraj/Desktop/screenshots/32 - Backend load balancer.png')

2. Fill in:

| Field | Value |
|-------|-------|
| Name | `TM-Backend-ALB` |
| Scheme | Internet-facing |
| IP address type | IPv4 |
| VPC | Default VPC |
| Availability Zones | Select ALL available AZs |
| Security group | `TM-Backend-SG` |
| Listener Protocol/Port | HTTP / 80 |
| Default action | Forward to → `TM-Backend-TG` |

3. Click **Create load balancer** — wait 2-3 minutes for it to become **Active**

![Backend ALB Active]('/Users/Vraj/Desktop/screenshots/32 - Backend load balancer.png')

**Copy and save the Backend ALB DNS name:**
```
TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com
```


#### Create Frontend ALB (TM-Frontend-ALB)

Repeat with:
- Name: `TM-Frontend-ALB`
- Security group: `TM-Frontend-SG`
- Forward to: `TM-Frontend-TG`

![Frontend ALB Active]('/Users/Vraj/Desktop/screenshots/45 Frontend ALB.png')

**Copy and save the Frontend ALB DNS name:**
```
TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com
```

![Frontend ALB DNS name]('/Users/Vraj/Desktop/screenshots/46 - Testing using ALB.png')

---

### Part C: Verify Target Health

After the ALBs are active, go to **Target Groups** → select each TG → click **Targets** tab.

Both instances in each group must show **Healthy** status. If they show Unhealthy, wait 2 minutes (health checks take time) and check that Nginx is running on each instance.

![Backend targets both Healthy]('/Users/Vraj/Desktop/screenshots/68 T7 TG Backend Health.png')
![Frontend targets both Healthy]('/Users/Vraj/Desktop/screenshots/67 T6 - TG frontend health.png')

**Test the Frontend ALB** by pasting the Frontend ALB DNS into your browser:

![App loading via Frontend ALB DNS]('/Users/Vraj/Desktop/screenshots/46 - Testing using ALB.png')

---

## Step 6: Domain Setup with Cloudflare

### Part 1: Add Domain to Cloudflare

1. Log into [cloudflare.com](https://cloudflare.com)
2. Click **Add a Site** → enter `draxil.site` → Click **Continue**
3. Select the **Free plan** → Click **Continue**
4. Cloudflare scans for existing DNS records → click **Continue**
5. Cloudflare shows you **two nameservers** — copy both

![Cloudflare nameservers to copy]('/Users/Vraj/Desktop/screenshots/48 - namecheap-nameservers-updated-cloudflare.png')

### Part 2: Update Nameservers at Namecheap

1. Log into [namecheap.com](https://namecheap.com)
2. Click **Domain List** → **Manage** next to `draxil.site`
3. Under **Nameservers** → change dropdown to **Custom DNS**
4. Paste both Cloudflare nameservers
5. Click the ✓ checkmark to save

![Namecheap nameservers updated to Cloudflare]('/Users/Vraj/Desktop/screenshots/49 - Verification from cloudflare for site .png')

> DNS propagation takes 5 minutes to 2 hours. Cloudflare sends an email when your domain is active.

### Part 3: Add DNS Records in Cloudflare

In Cloudflare → click **draxil.site** → click **DNS** → **Records**

#### Record 1 — A Record (root domain to Frontend EC2)

| Field | Value |
|-------|-------|
| Type | A |
| Name | `@` |
| IPv4 address | TM-Frontend-1 Public IP |
| Proxy status | Proxied (orange cloud ON) |

Click **Save**

![A record added in Cloudflare]('/Users/Vraj/Desktop/screenshots/50 -cloudflare-dns-A-record-root-domain.png')

#### Record 2 — CNAME (www to Frontend ALB)

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `www` |
| Target | `TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com` |
| Proxy status | Proxied (orange cloud ON) |

Click **Save**

![CNAME www record added]('/Users/Vraj/Desktop/screenshots/51- cloudflare-dns-CNAME-www-frontend-alb.png')

#### Record 3 — CNAME (api to Backend ALB)

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `api` |
| Target | `TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com` |
| Proxy status | Proxied (orange cloud ON) |

Click **Save**

![CNAME api record added]('/Users/Vraj/Desktop/screenshots/52 - cloudflare-dns-CNAME-api-backend-alb.png')

All 3 DNS records together:

![All 3 DNS records in Cloudflare]('/Users/Vraj/Desktop/screenshots/53 - Check cloudflare domain is active cloudflare-all-3-dns-records-together.png')

### Part 4: Configure SSL/TLS

1. In Cloudflare → click **SSL/TLS** in the left sidebar
2. Set encryption mode to **Flexible**

> **Why Flexible?** Our Nginx on EC2 only listens on port 80 (HTTP). "Full" mode requires Nginx to also listen on port 443 (HTTPS), which would cause Error 521. "Flexible" means Cloudflare handles HTTPS externally while connecting to EC2 via HTTP — the user's browser still gets the padlock.

![SSL set to Flexible mode]('/Users/Vraj/Desktop/screenshots/54 -cloudflare-ssl-flexible-mode-selected.png')

3. Click **Edge Certificates** → enable **Always Use HTTPS**
4. Also enable **Automatic HTTPS Rewrites**

![Always Use HTTPS enabled]('/Users/Vraj/Desktop/screenshots/55 - cloudflare-always-use-https-enabled.png' and '/Users/Vraj/Desktop/screenshots/56 - cloudflare-automatic-https-rewrites-on.png')

---

## Step 7: Final Verification

Once Cloudflare shows your domain as **Active**, test all endpoints:

### Test 1 — Frontend with HTTPS

Open `https://www.draxil.site` in your browser.

You should see:
- The TravelMemory React application loading
- A **padlock icon** in the browser address bar (HTTPS working)

![TravelMemory app at https://www.draxil.site with padlock]('/Users/Vraj/Desktop/screenshots/62 Test 1 Final Website from Frontend - Test www with HTTPS CNAME RECORD.png')

### Test 2 — HTTP redirects to HTTPS

Open `http://www.draxil.site` — it should automatically redirect to `https://www.draxil.site`.

![HTTP auto-redirected to HTTPS and SSL Certificate]('/Users/Vraj/Desktop/screenshots/63 Test 2 Final Website - Test HTTP Redirects to HTTPS.png' and '/Users/Vraj/Desktop/screenshots/66 T5-SSL Certificate Details.png')

### Test 3 — Backend API

Open `https://api.draxil.site` in your browser — should return a response from Node.js.

![Backend API response at api.draxil.site]('/Users/Vraj/Desktop/screenshots/64 T3 Backend api .png')

### Test 4 — End-to-End Functionality

Use the app to add a travel memory:
1. Fill in the trip details form
2. Click Submit
3. Verify the data appears in the list
4. Go to MongoDB Atlas → your cluster → **Browse Collections** → confirm the data is stored

![Travel memory successfully added and saved to MongoDB]('/Users/Vraj/Desktop/screenshots/65 T4 - Database is getting added in Database mongodb.png')

---

## Conclusion

The TravelMemory MERN application is now fully deployed with:

- **High availability** — 2 frontend + 2 backend EC2 instances, no single point of failure
- **Load balancing** — AWS ALBs distribute traffic evenly across instances
- **Custom domain** — `draxil.site` managed through Cloudflare
- **SSL/HTTPS** — Cloudflare provides free SSL with automatic HTTPS redirects
- **Process management** — PM2 keeps Node.js running 24/7 and restarts on crash
- **Reverse proxy** — Nginx efficiently proxies requests to Node.js on each backend

### Key URLs Summary

| Service | URL |
|---------|-----|
| Frontend | https://www.draxil.site |
| Root domain | https://draxil.site |
| Backend API | https://api.draxil.site |
| Frontend ALB | TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com |
| Backend ALB | TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com |

### Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| Error 521 | Cloudflare SSL set to "Full", EC2 only on port 80 | Change SSL to **Flexible** |
| Target Unhealthy | Nginx stopped or app crashed | `sudo systemctl restart nginx` and `pm2 restart tm-backend` |
| API calls fail | `url.js` pointing to wrong URL | Update to `https://api.draxil.site`, rebuild, redeploy |
| SSH refused | Security group port 22 not open | Check TM-Backend-SG inbound rules |

> **Note:** All EC2 instances, Load Balancers, and AWS infrastructure have been terminated after submission to avoid ongoing AWS charges. Screenshots in the `/screenshots` folder serve as proof of the complete working deployment.
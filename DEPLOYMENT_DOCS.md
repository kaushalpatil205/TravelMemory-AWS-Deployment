# Deployment Guide: Travel Memory Application

This document provides a step-by-step walkthrough to deploy the Travel Memory MERN application on AWS EC2, configured with NGINX reverse proxies, Application Load Balancing, and a custom domain via Cloudflare.

## Prerequisites
- An AWS Account.
- A Cloudflare Account with a registered custom domain.
- A MongoDB Atlas cluster (with a connection string).

---

## Step 1: Launch EC2 Instances

For scaling, we will launch multiple EC2 instances. In a basic setup, you can have 2 Frontend instances and 2 Backend instances.

1. Navigate to the **EC2 Dashboard** in your AWS Management Console.
![EC2 Dashboard](screenshots/6%20%20-%20Backend%20Instances.png)
2. Click **Launch Instance**. Choose an **Ubuntu Server 22.04 LTS** (or 24.04 LTS) AMI.
![Ubuntu Server](screenshots/10%20-%20Backend%20Instance%20setup%201%20.png)
3. Configure Security Group:
   - **SSH (Port 22)**: Allow from your IP.
   - **HTTP (Port 80)**: Allow from anywhere.
   - **HTTPS (Port 443)**: Allow from anywhere.
   - **Custom TCP (Port 3000)**: Allow from your ALB or anywhere.
   ![Backend Security Group](screenshots/1-%20Backend%20Security%20Group.png)
   ![Frontend Security Group](screenshots/2-%20Frontend%20Security%20Group.png)
4. Launch and download the PEM key pair. Repeat this to create multiple instances for high availability.
![Multiple Instances Running](screenshots/61%20-%20Both%20instance%20active%20.png)

---

## Step 2: Environment Setup connect to EC2

Click on instance and click on connect button.
![Connect to instance](screenshots/9%20-%20Accessing%20Backend%20Instance%201%20.png)

Install the required dependencies (Node.js, Git, NGINX) on all instances:
```bash
sudo apt update
sudo apt install -y curl git nginx
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```
![Installing Node.js](screenshots/11%20-%20Installing%20NodeJs.png)
![Node.js Installed](screenshots/12%20-%20NodeJS%20installed%20.png)

---

## Step 3: Backend Configuration & Deployment

### 1. Clone the repository in both backend instances
```bash
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/backend
```
![Cloned the repository](screenshots/15%20-%20Cloning%20Git%20Repo%20in%20Backend%20Instance%201%20.png)

### 2. Configure `.env`
Create a `.env` file in the `backend` directory:
```bash
nano .env
```
Connect to MongoDB Atlas and copy the connection string.
![MongoDB User](screenshots/3%20-%20MongoDB%20user.png)
![MongoDB IP Access](screenshots/4%20-%20IP%20Access%20list.png)
![MongoDB Connection String](screenshots/5%20-%20MONGODB%20connection%20string.png)

```env
PORT=3000
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/travelmemory?retryWrites=true&w=majority
```
![Added connection string to env](screenshots/17%20-%20Connecting%20Database%20to%20Backend%20Instance%20one.png)

### 3. Install Dependencies & PM2
```bash
npm install
sudo npm install -g pm2
pm2 start index.js --name "travel-backend"
pm2 save
pm2 startup
```
![NPM Install](screenshots/16%20-%20Installing%20NPM%20%20in%20Backend%20instance%201.png)
![Installing PM2](screenshots/18%20-%20Installing%20PM2.png)
![Backend Server Started](screenshots/%2019%20-%20Backend%20Server%20Started.png)
![PM2 Save](screenshots/22%20PM2%20Save.png)

### 4. Setup Nginx Reverse Proxy for Backend
Create an Nginx configuration file (`/etc/nginx/sites-available/backend`):
```bash
sudo nano /etc/nginx/sites-available/backend
```
setup reverse proxy for backend
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
        proxy_cache_bypass $http_upgrade;
    }
}
```
![Setup Reverse proxy](screenshots/24-%20nginx-reverse-proxy-config-backend1.png)

Link and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```
![Link and restart Nginx](screenshots/23%20-nginx-config-test-ok-backend1.png)

---

## Step 4: Frontend Configuration & Deployment

### 1. Update Frontend `url.js`
In the frontend instance, clone the project and navigate to the `frontend` folder:
```bash
git clone https://github.com/UnpredictablePrashant/TravelMemory.git
cd TravelMemory/frontend
```
![Clone Frontend Repo](screenshots/33%20-FRONTEND%20SETUP%20ON%20TM-Frontend-1.png)

Set your environment variable for production:
```bash
nano .env
```
Inside env file add the following:
```bash
REACT_APP_BACKEND_URL=http://<YOUR_BACKEND_IP>
```
![Update url.js](screenshots/36%20-url-js-updated-backend-alb-dns-frontend1.png)

### 2. Build the Application
```bash
npm install
npm run build
```
![NPM Install Frontend](screenshots/37%20-%20npm-install-frontend1-complete.png)
![Build Frontend](screenshots/38%20-%20npm-build-success-frontend1.png)

### 3. Serve Frontend via Nginx
Copy the built files to the NGINX web root:
```bash
sudo cp -r build/* /var/www/html/
```
![Copy build files](screenshots/39%20-%20files-copied-to-var-www-html-frontend1.png)

Update NGINX to serve the React application (`/etc/nginx/sites-available/default`):
```bash
sudo nano /etc/nginx/sites-available/default
```
```nginx
server {
    listen 80;

    root /var/www/html;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```
Restart Nginx: `sudo systemctl restart nginx`
![Frontend Config OK](screenshots/40%20-%20nginx-frontend-config-test-ok..png)

Now copy the frontend ip address and paste it in your browser.
![Frontend App Live](screenshots/41%20-%20travelmemory-app-browser-frontend1-ip.png)

---

## Step 5: Application Load Balancer Configuration

Part A : Create Target Groups
1. Navigate to Target Groups and click Create target group.
2. Choose Instances, Name it `frontend-tg`, HTTP/80.
3. Select the Frontend EC2 instances and Create target group.
![Frontend Target Group](screenshots/44%20Frontend%20TG.png)
4. Repeat for the Backend instances to create `backend-tg`.
![Backend Target Group](screenshots/30%20-%20BACKEND%20target%20groups.png)

Part B : Create Load Balancer
1. Go to Load Balancers -> Create Application Load Balancer.
2. Name it, scheme Internet-facing.
![Frontend ALB](screenshots/45%20Frontend%20ALB.png)
![Backend ALB](screenshots/32%20-%20Backend%20load%20balancer.png)

Part C : Route Testing
Test by sending traffic to the Load Balancer DNS names.
![Test ALB](screenshots/46%20-%20Testing%20using%20ALB.png)

---

## Step 6: Domain Setup with Cloudflare

Part 1: Connect your new domain to Cloudflare
1. Log into your registrar (like Namecheap) and change nameservers to Cloudflare.
![Domain buy](screenshots/47%20Domain%20buy%20.png)
![Nameservers](screenshots/48%20-%20namecheap-nameservers-updated-cloudflare.png)
![Active Status](screenshots/49%20-%20Verification%20from%20cloudflare%20for%20site%20.png)

Part 2: Add DNS Records
1. Add the CNAME Record for ALB.
![DNS A Record](screenshots/50%20-cloudflare-dns-A-record-root-domain.png)
![DNS CNAME WWW](screenshots/51-%20cloudflare-dns-CNAME-www-frontend-alb.png)
![DNS CNAME API](screenshots/52%20-%20cloudflare-dns-CNAME-api-backend-alb.png)
![All Records Together](screenshots/53%20-%20Check%20cloudflare%20domain%20is%20active%20cloudflare-all-3-dns-records-together.png)

Part 3: SSL Configuration
Switch SSL mode to Flexible.
![SSL Flexible Mode](screenshots/54%20-cloudflare-ssl-flexible-mode-selected.png)
Enable Always Use HTTPS and HTTPS Rewrites.
![Always Use HTTPS](screenshots/55%20-%20cloudflare-always-use-https-enabled.png)
![HTTPS Rewrites](screenshots/56%20-%20cloudflare-automatic-https-rewrites-on.png)

---

## Step 7: Final Tests and Health Checks

With instances connected to the Application Load balancer and routed through Cloudflare, the application is live and secured.

1. Website accessible via HTTPS CNAME
![Test 1](screenshots/62%20Test%201%20Final%20Website%20from%20Frontend%20-%20Test%20www%20with%20HTTPS%20CNAME%20RECORD.png)
2. HTTP successfully redirects to HTTPS
![Test 2](screenshots/63%20Test%202%20Final%20Website%20-%20Test%20HTTP%20Redirects%20to%20HTTPS.png)
3. Backend API reaches successfully
![Backend API](screenshots/64%20T3%20Backend%20api%20.png)
4. Database stores data
![Database Insert](screenshots/65%20T4%20-%20Database%20is%20getting%20added%20in%20Database%20mongodb.png)
5. SSL Certificate valid
![SSL Valid](screenshots/66%20T5-SSL%20Certificate%20Details.png)

Target Group Health Validations:
![TG Frontend Health](screenshots/67%20T6%20-%20TG%20frontend%20health.png)
![TG Backend Health](screenshots/68%20T7%20TG%20Backend%20Health.png)
![ALB Frontend Health](screenshots/69%20T9%20Test%20Load%20Balancer%20Health%20Frontend.png)
![ALB Backend Health](screenshots/70%20T10%20Test%20Load%20Balancer%20Health%20Backend.png)


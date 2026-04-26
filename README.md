### Load Balancer Health Check

Both ALBs showing Active, all 4 targets showing Healthy.

---

## Step 7 - Cloudflare Domain Setup

Domain purchased: **draxil.site** (Namecheap)

### Add Domain to Cloudflare
1. Created Cloudflare free account
2. Added draxil.site
3. Updated Namecheap nameservers to Cloudflare nameservers

### DNS Records

| Type | Name | Value |
|------|------|-------|
| A | @ | TM-Frontend-1 Public IP |
| CNAME | www | TM-Frontend-ALB-328778329.ap-south-1.elb.amazonaws.com |
| CNAME | api | TM-Backend-ALB-1289212996.ap-south-1.elb.amazonaws.com |

### SSL Configuration

Set SSL/TLS mode to **Flexible** (EC2 instances use HTTP on port 80, Cloudflare handles HTTPS termination externally).

Enabled:
- Always Use HTTPS ✅
- Automatic HTTPS Rewrites ✅

**Note on SSL 521 Error:** Initially configured as "Full" SSL mode which caused Error 521 because Cloudflare attempted HTTPS connection to EC2 on port 443, but Nginx only listens on port 80. Fixed by switching to "Flexible" mode.

---

## Step 8 - Final Testing

### Application Running with HTTPS

### Travel Memory Added Successfully

### All Tests Passed

| Test | URL | Result |
|------|-----|--------|
| Root domain | http://draxil.site | ✅ App loads |
| www with HTTPS | https://www.draxil.site | ✅ App loads with padlock |
| HTTP → HTTPS redirect | http://www.draxil.site | ✅ Redirects to HTTPS |
| Backend API | https://api.draxil.site | ✅ API responds |
| Backend targets | AWS Console | ✅ Both Healthy |
| Frontend targets | AWS Console | ✅ Both Healthy |
| End-to-end | Add travel memory | ✅ Saves to MongoDB |

---

## Nginx Configurations

### Backend — Reverse Proxy

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

### Frontend — React SPA

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

## Troubleshooting

### Error 521 — Web Server Down
**Cause:** Cloudflare SSL set to "Full" mode, EC2 Nginx only listens on port 80 not 443.
**Fix:** Change Cloudflare SSL mode from "Full" to "Flexible".

### PM2 App Shows "Errored"
```bash
pm2 logs tm-backend    # View error logs
cat .env               # Verify MongoDB URI is correct
pm2 restart tm-backend
```

### Target Group Shows "Unhealthy"
```bash
sudo systemctl status nginx    # Check Nginx
pm2 status                     # Check Node.js app
curl http://localhost/         # Test locally
sudo systemctl restart nginx
```

### React App API Calls Failing
```bash
cat ~/TravelMemory/frontend/src/url.js
# Must show: export const baseURL = "https://api.draxil.site"
# If wrong: fix → npm run build → sudo cp -r build/* /var/www/html/
```

---

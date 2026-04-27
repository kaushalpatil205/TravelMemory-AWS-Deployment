import urllib.parse
import re

with open('old_readme.md', 'r') as f:
    content = f.read()

# Architecture images
content = content.replace('![TravelMemory AWS Architecture](architecture/TravelMemory-AWS-Architecture.png)',
'''![TravelMemory AWS Architecture](architecture/travelmemory_draxil_site_architecture.png)
![TravelMemory Web Architecture](architecture/preview.webp)''')

replacements = {
    '02-key-pair-travelmemory-key-created.png': '',
    '03-TM-Backend-SG-inbound-rules.png': '1- Backend Security Group.png',
    '04-TM-Frontend-SG-inbound-rules.png': '2- Frontend Security Group.png',
    '06-mongodb-cluster-created.png': '3 - MongoDB user.png',
    '08-mongodb-network-access-allow-all.png': '4 - IP Access list.png',
    '10-all-4-ec2-instances-running.png': '6  - Backend Instances.png',
    '11-ec2-instances-public-ips-noted.png': '61 - Both instance active .png',
    '12-ssh-into-tm-backend-1.png': '9 - Accessing Backend Instance 1 .png',
    '13-nodejs-18-version-verified.png': '12 - NodeJS installed .png',
    '14-nginx-active-running-backend1.png': '13 - Nginx Server Started.png',
    '17-npm-install-backend-complete.png': '16 - Installing NPM  in Backend instance 1.png',
    '18-env-file-created-backend1.png': '17 - Connecting Database to Backend Instance one.png',
    '19-backend-server-started-mongodb-connected.png': ' 19 - Backend Server Started.png',
    '20-pm2-status-online-backend1.png': '20.1 - PM2 Online.png',
    '22-nginx-config-test-ok-backend1.png': '23 -nginx-config-test-ok-backend1.png',
    '58-url-js-updated-api-draxil-site-frontend1.png': '57 - url-js-updated-api-draxil-site-frontend1.png',
    '34-npm-build-success-frontend1.png': '38 - npm-build-success-frontend1.png',
    '37-travelmemory-app-browser-frontend1-ip.png': '41 - travelmemory-app-browser-frontend1-ip.png',
    '41-tm-backend-tg-created-both-instances.png': '30 - BACKEND target groups.png',
    '43-tm-backend-alb-active-status.png': '32 - Backend load balancer.png',
    '45-tm-frontend-alb-active-status.png': '45 Frontend ALB.png',
    '66-tm-backend-tg-both-targets-healthy.png': '68 T7 TG Backend Health.png',
    '67-tm-frontend-tg-both-targets-healthy.png': '67 T6 - TG frontend health.png',
    '50-namecheap-nameservers-updated-cloudflare.png': '48 - namecheap-nameservers-updated-cloudflare.png',
    '54-cloudflare-all-3-dns-records-together.png': '53 - Check cloudflare domain is active cloudflare-all-3-dns-records-together.png',
    '55-cloudflare-ssl-flexible-mode-selected.png': '54 -cloudflare-ssl-flexible-mode-selected.png',
    '72-error-521-before-fix.png': '',
    '73-ssl-changed-to-flexible-fix.png': '',
    '63-app-loading-https-www-draxil-site-padlock.png': '62 Test 1 Final Website from Frontend - Test www with HTTPS CNAME RECORD.png',
    '70-travel-memory-added-successfully.png': '65 T4 - Database is getting added in Database mongodb.png'
}

def encode_path(filename):
    if not filename:
        return ""
    return "screenshots/" + urllib.parse.quote(filename)

for old, new in replacements.items():
    if not new:
        # Remove the entire markdown image tag if there's no replacement
        content = re.sub(r'!\[.*?\]\(screenshots/' + re.escape(old) + r'\)\n?', '', content)
    else:
        # Replace the image path
        content = content.replace(f'screenshots/{old}', encode_path(new))

# Write to README.md
with open('README.md', 'w') as f:
    f.write(content)


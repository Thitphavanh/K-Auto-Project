# 📘 ຄູ່ມືການ Deploy ໂປຣເຈັກໄປ DigitalOcean ດ້ວຍ Docker

ຄູ່ມືນີ້ຈະແນະນຳວິທີການ Deploy โປຣເຈັກ K-Auto (Django + PostgreSQL + Redis + Daphne) ໄປຍັງ DigitalOcean ໂດຍໃຊ້ Docker ແລະ Docker Compose.

---

## 📋 ສາລະບານ

1. [ຂໍ້ກໍານົດເບື້ອງຕົ້ນ](#ຂໍ້ກໍານົດເບື້ອງຕົ້ນ)
2. [ຂັ້ນຕອນທີ 1: ສ້າງ Droplet ໃນ DigitalOcean](#ຂັ້ນຕອນທີ-1-ສ້າງ-droplet-ໃນ-digitalocean)
3. [ຂັ້ນຕອນທີ 2: ເຊື່ອມຕໍ່ກັບ Server](#ຂັ້ນຕອນທີ-2-ເຊື່ອມຕໍ່ກັບ-server)
4. [ຂັ້ນຕອນທີ 3: ຕິດຕັ້ງ Docker ແລະ Docker Compose](#ຂັ້ນຕອນທີ-3-ຕິດຕັ້ງ-docker-ແລະ-docker-compose)
5. [ຂັ້ນຕອນທີ 4: ສ້າງໂຄງສ້າງໂປຣເຈັກ](#ຂັ້ນຕອນທີ-4-ສ້າງໂຄງສ້າງໂປຣເຈັກ)
6. [ຂັ້ນຕອນທີ 5: ຕັ້ງຄ່າໄຟລ໌ Configuration](#ຂັ້ນຕອນທີ-5-ຕັ້ງຄ່າໄຟລ໌-configuration)
7. [ຂັ້ນຕອນທີ 6: Deploy Application](#ຂັ້ນຕອນທີ-6-deploy-application)
8. [ຂັ້ນຕອນທີ 7: ຕິດຕັ້ງ SSL Certificate](#ຂັ້ນຕອນທີ-7-ຕິດຕັ້ງ-ssl-certificate)
9. [ຂັ້ນຕອນທີ 8: ຕັ້ງຄ່າ Firewall](#ຂັ້ນຕອນທີ-8-ຕັ້ງຄ່າ-firewall)
10. [ຄຳສັ່ງທີ່ໃຊ້ເລື້ອຍໆ](#ຄຳສັ່ງທີ່ໃຊ້ເລື້ອຍໆ)
11. [Troubleshooting](#troubleshooting)

---

## ຂໍ້ກໍານົດເບື້ອງຕົ້ນ

### ບົນ Local Machine
- Git
- SSH Key ສຳລັບການເຂົ້າ Server
- Domain Name (ຖ້າຕ້ອງການໃຊ້ SSL)

### ບົນ DigitalOcean
- ບັນຊີ [DigitalOcean](https://www.digitalocean.com)
- Droplet (ແນະນຳ: 2GB RAM ຂື້ນໄປ)

### ໂຄງສ້າງໂປຣເຈັກ

```
K-Auto-Project/
├── config/              # Django settings
├── apps/                # Django apps
├── static/              # Static files
├── media/               # Media files
├── docker-compose.yml   # Development config
├── docker-compose.prod.yml  # Production config (ຈະສ້າງ)
├── Dockerfile           # Docker image
├── requirements.txt     # Python dependencies
├── .env.production      # Production environment variables (ຈະສ້າງ)
└── nginx/              # Nginx configuration (ຈະສ້າງ)
    └── nginx.conf
```

---

## ຂັ້ນຕອນທີ 1: ສ້າງ Droplet ໃນ DigitalOcean

### 1.1 ເຂົ້າສູ່ລະບົບແລະສ້າງ Droplet

1. ເຂົ້າສູ່ລະບົບ [DigitalOcean Dashboard](https://cloud.digitalocean.com)
2. ກົດ **Create** → **Droplets**
3. ເລືອກການຕັ້ງຄ່າດັ່ງນີ້:

#### Distribution
- **OS**: Ubuntu 22.04 LTS x64

#### Plan
- **Basic Plan**: $6/month ຂື້ນໄປ
- **CPU Options**: Regular with SSD
- **RAM**: 2GB ຂື້ນໄປ (4GB ແນະນຳສຳລັບ production)
- **Storage**: 50GB SSD ຂື້ນໄປ

#### Datacenter Region
- **Singapore**: ສຳລັບເອເຊຍຕາເວັນອອກສຽງໃຕ້
- **Frankfurt**: ສຳລັບເອີຣົບ
- **New York**: ສຳລັບອາເມລິກາ

#### Authentication
- **SSH Keys**: ແນະນຳ (ປອດໄພກວ່າ)
- **Password**: ສຳຮອງ

#### Hostname
- ຕັ້ງຊື່ເຊັ່ນ: `kauto-production`

4. ກົດ **Create Droplet**
5. ລໍຖ້າ 1-2 ນາທີ ແລ້ວບັນທຶກ IP address ຂອງ Droplet

---

## ຂັ້ນຕອນທີ 2: ເຊື່ອມຕໍ່ກັບ Server

### 2.1 ເຊື່ອມຕໍ່ຜ່ານ SSH

```bash
# ຖ້າໃຊ້ SSH Key
ssh root@your_droplet_ip

# ຖ້າໃຊ້ Password
ssh root@your_droplet_ip
# ໃສ່ລະຫັດຜ່ານທີ່ໄດ້ຮັບທາງອີເມລ
```

### 2.2 ອັບເດດລະບົບ

```bash
apt update && apt upgrade -y
```

---

## ຂັ້ນຕອນທີ 3: ຕິດຕັ້ງ Docker ແລະ Docker Compose

### 3.1 ຕິດຕັ້ງ Dependencies

```bash
apt install -y apt-transport-https ca-certificates curl software-properties-common git
```

### 3.2 ຕິດຕັ້ງ Docker

```bash
# ເພີ່ມ Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# ເພີ່ມ Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# ອັບເດດ package list
apt update

# ຕິດຕັ້ງ Docker
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 3.3 ກວດສອບການຕິດຕັ້ງ

```bash
docker --version
# ຜົນລັບ: Docker version 24.x.x

docker compose version
# ຜົນລັບ: Docker Compose version v2.x.x
```

### 3.4 ເລີ່ມແລະເປີດໃຊ້ Docker Service

```bash
systemctl start docker
systemctl enable docker
```

---

## ຂັ້ນຕອນທີ 4: ສ້າງໂຄງສ້າງໂປຣເຈັກ

### 4.1 ສ້າງ Directory ສຳລັບໂປຣເຈັກ

```bash
mkdir -p /var/www/kauto
cd /var/www/kauto
```

### 4.2 Upload ໂປຣເຈັກ (ເລືອກວິທີໃດວິທີໜຶ່ງ)

#### ວິທີທີ 1: ໃຊ້ Git Clone (ແນະນຳ)

```bash
# Clone ຈາກ repository
git clone https://github.com/your-username/K-Auto-Project.git .

# ຫຼື ຖ້າໃຊ້ private repository
git clone git@github.com:your-username/K-Auto-Project.git .
```

#### ວິທີທີ 2: ໃຊ້ SCP Upload ຈາກເຄື່ອງ Local

ຈາກເຄື່ອງ Local ຂອງທ່ານ:

```bash
# Upload ທັງໝົດໂປຣເຈັກ (ບໍ່ລວມ virtual environment ແລະ __pycache__)
rsync -avz --progress \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'media/*' \
  /Users/hery/My-Project/K-Auto-Project/autoparts/ \
  root@your_droplet_ip:/var/www/kauto/
```

#### ວິທີທີ 3: ໃຊ້ SFTP Client (FileZilla, Cyberduck)

1. ເປີດ SFTP Client
2. ເຊື່ອມຕໍ່ກັບ `your_droplet_ip` port `22`
3. Upload ໂຟລເດີໂປຣເຈັກໄປທີ່ `/var/www/kauto/`

---

## ຂັ້ນຕອນທີ 5: ຕັ້ງຄ່າໄຟລ໌ Configuration

### 5.1 ສ້າງໄຟລ໌ .env.production

```bash
cd /var/www/kauto
nano .env.production
```

ເພີ່ມເນື້ອຫາດັ່ງນີ້:

```env
# Django Settings
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=@ppwz5mw*=ts!waq%qx9$6!q-jsbmw^bb*(40)wug66-7=6v87
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your_droplet_ip

# Database Configuration
DB_NAME=kauto_db
DB_USER=postgres
DB_PASSWORD=72EWAzWc#nlVv#krO@C!MtxpUi@ayqyr
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Security Settings
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email Configuration (ຖ້າໃຊ້)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

**ບັນທຶກ**: ກົດ `Ctrl+X`, ແລ້ວ `Y`, ແລ້ວ `Enter` ເພື່ອບັນທຶກ

**ສຳຄັນ**:
- ປ່ຽນ `SECRET_KEY` ເປັນຄ່າທີ່ແຂງແຮງ (ໃຊ້ຄ່າທີ່ສ້າງໃໝ່)
- ປ່ຽນ `DB_PASSWORD` ເປັນລະຫັດທີ່ແຂງແຮງ
- ປ່ຽນ `yourdomain.com` ແລະ `your_droplet_ip` ເປັນຄ່າຈິງ

### 5.2 ສ້າງ Docker Compose Production File

ໄຟລ໌ນີ້ຄວນມີຢູ່ແລ້ວໃນໂປຣເຈັກ. ຖ້າບໍ່ມີ:

```bash
nano docker-compose.prod.yml
```

ເພີ່ມເນື້ອຫາ (ຕົວຢ່າງຢູ່ທ້າຍເອກະສານ)

---

## ຂັ້ນຕອນທີ 6: Deploy Application

### 6.1 ກວດສອບໂຄງສ້າງໄຟລ໌

```bash
cd /var/www/kauto
ls -la
```

ຕ້ອງມີໄຟລ໌ເຫຼົ່ານີ້:
- `Dockerfile`
- `docker-compose.prod.yml`
- `.env.production`
- `nginx/nginx.conf`
- `manage.py`
- `requirements.txt`

### 6.2 Build ແລະ Start Containers

```bash
# Build images ແລະ start containers
docker compose -f docker-compose.prod.yml up -d --build

# ລໍຖ້າ 2-5 ນາທີສຳລັບການ build
```

### 6.3 ກວດສອບສະຖານະ Containers

```bash
# ເບິ່ງສະຖານະ
docker compose -f docker-compose.prod.yml ps

# ຜົນລັບຄວນເປັນ:
# NAME          STATUS         PORTS
# kauto_db      Up (healthy)   5432/tcp
# kauto_redis   Up (healthy)   6379/tcp
# kauto_web     Up             8000/tcp
# kauto_nginx   Up             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 6.4 ເບິ່ງ Logs

```bash
# ເບິ່ງ logs ທັງໝົດ
docker compose -f docker-compose.prod.yml logs -f

# ເບິ່ງ logs ສະເພາະ service
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f db
docker compose -f docker-compose.prod.yml logs -f nginx
```

### 6.5 Run Migrations

```bash
# Run database migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files (ຖ້າຍັງບໍ່ໄດ້ເຮັດອັດຕະໂນມັດ)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 6.6 ສ້າງ Superuser

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

ປ້ອນຂໍ້ມູນ:
- Username
- Email
- Password (ຕ້ອງໃສ່ 2 ເທື່ອເພື່ອຢືນຢັນ)

### 6.7 ທົດສອບການເຂົ້າເວັບໄຊ

ເປີດ browser ແລ້ວໄປທີ່:
- `http://your_droplet_ip` (ຄວນເຫັນໜ້າເວັບ)
- `http://your_droplet_ip/admin` (ຄວນເຫັນໜ້າ Django Admin)

---

## ຂັ້ນຕອນທີ 7: ຕິດຕັ້ງ SSL Certificate

### 7.1 ຕັ້ງຄ່າ DNS

ກ່ອນອື່ນ, ຕ້ອງຕັ້ງຄ່າ DNS records:

1. ເຂົ້າໄປທີ່ DNS provider ຂອງທ່ານ (Namecheap, GoDaddy, Cloudflare, etc.)
2. ສ້າງ A records:

   | Type | Name | Value           | TTL  |
   |------|------|-----------------|------|
   | A    | @    | YOUR_DROPLET_IP | 3600 |
   | A    | www  | YOUR_DROPLET_IP | 3600 |

3. ລໍຖ້າ DNS propagation (5-30 ນາທີ)

### 7.2 ກວດສອບ DNS

```bash
# ກວດສອບວ່າ DNS ຊີ້ຖືກຕ້ອງແລ້ວ
dig yourdomain.com +short
# ຄວນໄດ້ IP ຂອງ Droplet

nslookup yourdomain.com
```

### 7.3 ຕິດຕັ້ງ Certbot

```bash
# ຕິດຕັ້ງ Certbot
apt install -y certbot python3-certbot-nginx

# ຫຼື ໃຊ້ snap (ແນະນຳ)
snap install --classic certbot
ln -s /snap/bin/certbot /usr/bin/certbot
```

### 7.4 Stop Nginx Container ຊົ່ວຄາວ

```bash
# Stop nginx ເພື່ອໃຫ້ Certbot ໃຊ້ port 80
docker compose -f docker-compose.prod.yml stop nginx
```

### 7.5 ສ້າງ SSL Certificate

```bash
# ສ້າງ certificate
certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

### 7.6 Copy Certificates

```bash
# ສ້າງໂຟລເດີສຳລັບ SSL
mkdir -p /var/www/kauto/nginx/ssl

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /var/www/kauto/nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /var/www/kauto/nginx/ssl/

# ຕັ້ງສິດອ່ານ
chmod 644 /var/www/kauto/nginx/ssl/fullchain.pem
chmod 600 /var/www/kauto/nginx/ssl/privkey.pem
```

### 7.7 ອັບເດດ Nginx Configuration

ແກ້ໄຂໄຟລ໌ `nginx/nginx.conf` ເພື່ອເປີດໃຊ້ HTTPS (ດູຕົວຢ່າງທ້າຍເອກະສານ)

### 7.8 Start Nginx ອີກຄັ້ງ

```bash
# Start nginx ດ້ວຍການຕັ້ງຄ່າໃໝ່
docker compose -f docker-compose.prod.yml up -d nginx

# ກວດສອບ logs
docker compose -f docker-compose.prod.yml logs nginx
```

### 7.9 ທົດສອບ HTTPS

ເປີດ browser:
- `https://yourdomain.com` (ຄວນເຫັນ 🔒 ໃນ address bar)
- `http://yourdomain.com` (ຄວນ redirect ໄປ HTTPS)

### 7.10 ຕັ້ງການຕໍ່ອາຍຸອັດຕະໂນມັດ

```bash
# ທົດສອບການຕໍ່ອາຍຸ
certbot renew --dry-run

# ຖ້າສຳເລັດ, ຕັ້ງ cron job
crontab -e
```

ເພີ່ມບັນທັດນີ້:

```cron
# ຕໍ່ອາຍຸ SSL ທຸກໆ 2 ເດືອນ (ເວລາ 2 ໂມງເຊົ້າ)
0 2 1 */2 * certbot renew --quiet --deploy-hook "docker compose -f /var/www/kauto/docker-compose.prod.yml restart nginx"
```

---

## ຂັ້ນຕອນທີ 8: ຕັ້ງຄ່າ Firewall

### 8.1 ເປີດໃຊ້ UFW Firewall

```bash
# ອະນຸຍາດ OpenSSH ກ່ອນ (ສຳຄັນ!)
ufw allow OpenSSH

# ອະນຸຍາດ HTTP ແລະ HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# ເປີດໃຊ້ firewall
ufw enable

# ກົດ 'y' ເພື່ອຢືນຢັນ
```

### 8.2 ກວດສອບສະຖານະ

```bash
# ເບິ່ງສະຖານະ firewall
ufw status

# ຜົນລັບ:
# Status: active
# To                         Action      From
# --                         ------      ----
# OpenSSH                    ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

---

## ຄຳສັ່ງທີ່ໃຊ້ເລື້ອຍໆ

### ການຈັດການ Containers

```bash
# ເບິ່ງສະຖານະ
docker compose -f docker-compose.prod.yml ps

# ເບິ່ງ logs
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f web

# Restart services
docker compose -f docker-compose.prod.yml restart
docker compose -f docker-compose.prod.yml restart web

# Stop services
docker compose -f docker-compose.prod.yml stop

# Start services
docker compose -f docker-compose.prod.yml start

# Stop ແລະລຶບ containers
docker compose -f docker-compose.prod.yml down

# Rebuild ແລະ restart
docker compose -f docker-compose.prod.yml up -d --build
```

### ການອັບເດດໂປຣເຈັກ

```bash
# ວິທີທີ 1: ໃຊ້ Git
cd /var/www/kauto
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build web

# Run migrations ຖ້າມີ
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Restart
docker compose -f docker-compose.prod.yml restart web
```

### ການຈັດການ Database

```bash
# ເຂົ້າ PostgreSQL shell
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d kauto_db

# Backup database
docker compose -f docker-compose.prod.yml exec db pg_dump -U postgres kauto_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U postgres kauto_db

# ເບິ່ງຂະໜາດ database
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d kauto_db -c "SELECT pg_size_pretty(pg_database_size('kauto_db'));"
```

### ການຈັດການໄຟລ໌ Static ແລະ Media

```bash
# Collect static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# ກວດສອບ permissions
docker compose -f docker-compose.prod.yml exec web ls -la /app/staticfiles
docker compose -f docker-compose.prod.yml exec web ls -la /app/media
```

### Django Management Commands

```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Django shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# ລຶບ sessions ເກົ່າ
docker compose -f docker-compose.prod.yml exec web python manage.py clearsessions

# ກວດສອບ deployment readiness
docker compose -f docker-compose.prod.yml exec web python manage.py check --deploy
```

### Monitoring

```bash
# ເບິ່ງການໃຊ້ resources
docker stats

# ເບິ່ງ disk usage
docker system df
df -h

# ເບິ່ງ memory usage
free -h

# ລຶບ images ທີ່ບໍ່ໄດ້ໃຊ້
docker system prune -a
```

---

## Troubleshooting

### 1. Site ບໍ່ສາມາດເຂົ້າເຖິງໄດ້

```bash
# ກວດສອບວ່າ containers ກຳລັງເຮັດວຽກ
docker compose -f docker-compose.prod.yml ps

# ກວດສອບ logs
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs web

# ກວດສອບ firewall
ufw status

# Test ຈາກ server
curl http://localhost
curl http://localhost:8000
```

### 2. Database Connection Error

```bash
# ກວດສອບ database container
docker compose -f docker-compose.prod.yml ps db

# ກວດສອບ logs
docker compose -f docker-compose.prod.yml logs db

# Test connection
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d kauto_db -c "SELECT 1;"

# ກວດສອບ environment variables
docker compose -f docker-compose.prod.yml exec web env | grep DB
```

### 3. Static Files ບໍ່ສະແດງ

```bash
# Collect static files ໃໝ່
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# ກວດສອບ nginx config
docker compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/nginx.conf

# Test nginx configuration
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### 4. Out of Memory

```bash
# ກວດສອບ memory usage
free -h
docker stats

# ເພີ່ມ swap space
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

### 5. SSL Certificate Issues

```bash
# ກວດສອບ certificates
certbot certificates

# ທົດສອບການຕໍ່ອາຍຸ
certbot renew --dry-run

# ກວດສອບວ່າ domain ຊີ້ໄປ IP ຖືກຕ້ອງ
dig yourdomain.com
```

---

## ຂໍ້ແນະນຳດ້ານຄວາມປອດໄພ

1. **ໃຊ້ Strong Passwords**
   - Database password
   - Django secret key
   - Superuser password

2. **ອັບເດດ Firewall Rules**
   ```bash
   ufw default deny incoming
   ufw default allow outgoing
   ufw allow OpenSSH
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

3. **ປິດ Debug Mode**
   - ຕັ້ງ `DEBUG=False` ໃນ `.env.production`

4. **ເກັບຮັກສາ Secrets**
   - ຢ່າ commit `.env.production` ເຂົ້າ Git
   - ໃຊ້ `.env.production.example` ແທນ

5. **Regular Security Updates**
   ```bash
   apt update && apt upgrade -y
   ```

---

## Backup Strategy

### Automated Backup Script

ສ້າງໄຟລ໌ `/root/backup-kauto.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# ສ້າງໂຟລເດີ backup
mkdir -p $BACKUP_DIR

# Backup database
docker compose -f /var/www/kauto/docker-compose.prod.yml exec -T db pg_dump -U postgres kauto_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/kauto/media

# ລຶບ backups ເກົ່າກວ່າ 7 ວັນ
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

ເຮັດໃຫ້ script executable:

```bash
chmod +x /root/backup-kauto.sh
```

ຕັ້ງ cron job:

```bash
crontab -e
```

ເພີ່ມ:

```cron
# Backup ທຸກວັນເວລາ 2 ໂມງເຊົ້າ
0 2 * * * /root/backup-kauto.sh >> /var/log/backup-kauto.log 2>&1
```

---

## Checklist ສຳລັບ Production

- [ ] ປ່ຽນ `SECRET_KEY` ເປັນຄ່າທີ່ແຂງແຮງ
- [ ] ຕັ້ງ `DEBUG=False`
- [ ] ອັບເດດ `ALLOWED_HOSTS` ດ້ວຍ domain ຈິງ
- [ ] ປ່ຽນ `DB_PASSWORD` ເປັນລະຫັດທີ່ແຂງແຮງ
- [ ] ຕັ້ງຄ່າ DNS ຊີ້ໄປຫາ Droplet IP
- [ ] ຕິດຕັ້ງ SSL Certificate
- [ ] ເປີດ Firewall (UFW)
- [ ] ຕັ້ງການ backup ອັດຕະໂນມັດ
- [ ] ທົດສອບ application ທຸກຫນ້າ
- [ ] ກວດສອບ logs ວ່າບໍ່ມີ errors
- [ ] ທົດສອບການ upload ໄຟລ໌
- [ ] ທົດສອບການສົ່ງອີເມລ (ຖ້າໃຊ້)
- [ ] ສ້າງ superuser account
- [ ] ທົດສອບ admin panel
- [ ] ກວດສອບ static files ໂຫຼດຖືກຕ້ອງ
- [ ] ທົດສອບ HTTPS redirect
- [ ] ຕັ້ງ monitoring

---

**ສຳເລັດ!** ໂປຣເຈັກຂອງທ່ານຄວນ online ແລ້ວ.

ຖ້າມີບັນຫາ ຫຼື ຄຳຖາມ, ກະລຸນາກວດສອບສ່ວນ Troubleshooting ຂ້າງເທິງ.

---

## ພາກຜະນວກ: ຕົວຢ່າງໄຟລ໌ Configuration

### A. ໄຟລ໌ docker-compose.prod.yml

```yaml
services:
  # PostgreSQL Database (Production)
  db:
    image: postgres:16-alpine
    container_name: kauto_db_prod
    volumes:
      - postgres_data_prod:/var/lib/postgresql/data
      - ./backups:/backups
    environment:
      - POSTGRES_DB=${DB_NAME:-kauto_db}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - kauto-network

  # Redis Cache & Channel Layer (Production)
  redis:
    image: redis:7-alpine
    container_name: kauto_redis_prod
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data_prod:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - kauto-network

  # Django Web Application (Production)
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: kauto_web_prod
    command: sh -c "python manage.py collectstatic --noinput && python manage.py migrate && daphne -b 0.0.0.0 -p 8000 config.asgi:application"
    volumes:
      - static_volume_prod:/app/staticfiles
      - media_volume_prod:/app/media
      - ./logs:/app/logs
    env_file:
      - .env.prod
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - kauto-network

  # Nginx Web Server & Reverse Proxy (Production)
  nginx:
    image: nginx:alpine
    container_name: kauto_nginx_prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume_prod:/app/staticfiles:ro
      - media_volume_prod:/app/media:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - kauto-network

volumes:
  postgres_data_prod:
  redis_data_prod:
  static_volume_prod:
  media_volume_prod:

networks:
  kauto-network:
    driver: bridge
```

### B. ໄຟລ໌ nginx/nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    client_max_body_size 100M;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;
        charset utf-8;

        # Static files
        location /static/ {
            alias /app/staticfiles/;
        }

        # Media files
        location /media/ {
            alias /app/media/;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://django;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Django application
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### C. ໄຟລ໌ .env.prod (ຕົວຢ່າງ)

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your_droplet_ip

# Database
DB_NAME=kauto_db
DB_USER=postgres
DB_PASSWORD=your-secure-database-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Security (ເປີດເມື່ອມີ SSL)
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

© 2024 K-Auto Project

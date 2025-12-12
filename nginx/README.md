# Nginx Configuration

ໂຟລເດີນີ້ມີການຕັ້ງຄ່າ Nginx ສຳລັບ production deployment.

## ໂຄງສ້າງໂຟລເດີ

```
nginx/
├── nginx.conf          # Main Nginx configuration
├── ssl/               # SSL certificates (ຈະສ້າງເມື່ອ deploy)
│   ├── fullchain.pem  # SSL certificate
│   └── privkey.pem    # Private key
├── logs/              # Nginx logs
│   ├── access.log
│   └── error.log
└── README.md          # This file
```

## ການນຳໃຊ້

### 1. ກ່ອນມີ SSL Certificate

ໃຊ້ຕໍ່າໄຟລ໌ `nginx.conf` ແລະເຂົ້າ browser ດ້ວຍ HTTP:
- `http://your_droplet_ip`
- `http://yourdomain.com`

### 2. ຫຼັງຈາກມີ SSL Certificate

1. Edit `nginx.conf`
2. ປ່ຽນ `yourdomain.com` ເປັນ domain ຈິງ
3. ລຶບ comment `#` ອອກຈາກສ່ວນ HTTPS server block
4. Restart nginx:
   ```bash
   docker compose -f docker-compose.prod.yml restart nginx
   ```

### 3. ທົດສອບ Configuration

```bash
# Test nginx config
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload nginx (ຖ້າ test ຜ່ານ)
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## ບັນທຶກສຳຄັນ

- ໂຟລເດີ `ssl/` ແລະ `logs/` ຈະຖືກສ້າງອັດຕະໂນມັດເມື່ອ deploy
- ຢ່າ commit ໄຟລ໌ SSL certificates ເຂົ້າ Git
- ຢ່າ commit ໄຟລ໌ logs ເຂົ້າ Git

## Troubleshooting

### ບັນຫາ: 502 Bad Gateway

```bash
# ກວດສອບວ່າ web container ກຳລັງເຮັດວຽກ
docker compose -f docker-compose.prod.yml ps web

# ກວດສອບ logs
docker compose -f docker-compose.prod.yml logs web
docker compose -f docker-compose.prod.yml logs nginx
```

### ບັນຫາ: Static files ບໍ່ໂຫຼດ

```bash
# Collect static files ໃໝ່
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Restart nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### ບັນຫາ: SSL Certificate Errors

```bash
# ກວດສອບວ່າໄຟລ໌ certificate ມີ
ls -la nginx/ssl/

# ກວດສອບ permissions
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

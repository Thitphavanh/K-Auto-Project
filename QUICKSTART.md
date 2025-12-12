# 🚀 Quick Start Guide - K-Auto Parts

## ເລີ່ມຕົ້ນງ່າຍໆ ພຽງ 3 ຂັ້ນຕອນ!

### ✅ ຂັ້ນຕອນທີ 1: Build Docker Images

```bash
docker compose build
```

ຫຼື ໃຊ້ Makefile:

```bash
make build
```

### ✅ ຂັ້ນຕອນທີ 2: Start Services

```bash
docker compose up
```

ຫຼື run ໃນພາກຫຼັງ:

```bash
docker compose up -d
```

ຫຼື ໃຊ້ Makefile:

```bash
make up
# ຫຼື
make up-d  # ຮັນພາກຫຼັງ
```

### ✅ ຂັ້ນຕອນທີ 3: Access Application

ເປີດ browser ແລະໄປທີ່:

- **ໜ້າຫຼັກ**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`
- **PostgreSQL**: localhost:54320
  - Database: `kauto_db`
  - User: `postgres`
  - Password: `postgres`
- **Redis**: localhost:6379

---

## 📊 ເພີ່ມຂໍ້ມູນຕົວຢ່າງ

```bash
docker compose exec web python manage.py populate_data
```

ຫຼື:

```bash
make populate
```

---

## 🎯 Commands ທີ່ໃຊ້ເລື້ອຍໆ

### ເບິ່ງ Logs

```bash
# ທັງໝົດ
make logs

# ສະເພາະ web
make logs-web

# ສະເພາະ database
make logs-db

# ສະເພາະ Redis
make logs-redis
```

### ເຂົ້າສູ່ Django Shell

```bash
make shell
```

### ເຂົ້າສູ່ Container Bash

```bash
make bash
```

### ເຮັດ Migrations

```bash
make makemigrations
make migrate
```

### ສ້າງ Superuser

```bash
make createsuperuser
```

### Restart Services

```bash
make restart
```

### Stop Services

```bash
make down
```

### ລ້າງຂໍ້ມູນທັງໝົດ (ລະວັງ!)

```bash
make clean
```

---

## 🔧 Troubleshooting

### ບັນຫາ: Port 8000 ຖືກໃຊ້ຢູ່ແລ້ວ

```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# ຫຼື ປ່ຽນ port ໃນ docker compose.yml
ports:
  - "8001:8000"
```

### ບັນຫາ: Database connection error

```bash
make logs-db  # ເບິ່ງ logs
make restart  # Restart services
```

### ບັນຫາ: Redis connection error

```bash
make logs-redis  # ເບິ່ງ logs
make restart    # Restart services
```

---

## 📱 Real-time Features ເຮັດວຽກແລ້ວ!

- ເປີດຫຼາຍໆ tab ໃນ browser
- ຂາຍສິນຄ້າໃນ POS (http://localhost:8000/pos/)
- ເບິ່ງສະຕັອກອັບເດດທັນທີໃນໜ້າຫຼັກ ແລະ ໜ້າສິນຄ້າ! 🎉

---

## 🎨 ທົດສອບ Features

### 1. ທົດສອບ POS System
1. ໄປທີ່: http://localhost:8000/pos/
2. Login ດ້ວຍ admin/admin123
3. ຍິງບາໂຄດ (ຫຼືພິມ barcode): BP001
4. ກົດ Enter
5. ເບິ່ງການອັບເດດແບບ Real-time!

### 2. ທົດສອບ Stock Management
1. ໄປທີ່: http://localhost:8000/stock-in/
2. ຍິງບາໂຄດເພື່ອເພີ່ມສະຕັອກ
3. ເບິ່ງການອັບເດດທັນທີ!

### 3. ທົດສອບ Product List
1. ໄປທີ່: http://localhost:8000/products/
2. ຄົ້ນຫາ, ກັ່ນຕອງ, ຈັດລຽງສິນຄ້າ
3. ເບິ່ງສະຕັອກອັບເດດແບບ Real-time!

### 4. ທົດສອບ Dark Mode
1. ກົດປຸ່ມ 🌙/☀️ ຢູ່ navbar
2. ເບິ່ງການປ່ຽນແປງທັນທີ!

### 5. ທົດສອບ Multi-language
1. ກົດປຸ່ມພາສາຢູ່ navbar
2. ເລືອກ: ລາວ, ໄທ, ຫຼື English
3. ເບິ່ງການແປພາສາທັນທີ!

---

## 🎉 ສຳເລັດ!

ລະບົບ K-Auto Parts ພ້ອມໃຊ້ງານແລ້ວ!

ສຳລັບເອກະສານເພີ່ມເຕີມ, ເບິ່ງທີ່ README.md

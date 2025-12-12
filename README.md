# K-Auto Parts Management System

ລະບົບຄຸ້ມຄອງອາໄຫຼ່ລົດທີ່ທັນສະໄໝ ດ້ວຍ Django, PostgreSQL, Redis ແລະ Real-time WebSocket

## 🚀 Features

- ✅ ລະບົບຂາຍສິນຄ້າ (POS) ດ້ວຍການສະແກນບາໂຄດ
- ✅ ຄຸ້ມຄອງສະຕັອກສິນຄ້າແບບ Real-time
- ✅ Dashboard ສະຫຼຸບຍອດຂາຍ ແລະ ກຣາຟ
- ✅ ຮອງຮັບ 3 ພາສາ: ລາວ, ໄທ, ອັງກິດ
- ✅ WebSocket ສຳລັບການອັບເດດແບບ Real-time
- ✅ Docker support
- ✅ PostgreSQL Database
- ✅ Redis Cache & Channel Layer
- ✅ Dark Mode

## 📋 Requirements

- Docker & Docker Compose
- Python 3.12+ (ຖ້າບໍ່ໃຊ້ Docker)
- PostgreSQL 16+ (ຖ້າບໍ່ໃຊ້ Docker)
- Redis 7+ (ຖ້າບໍ່ໃຊ້ Docker)

## 🔧 Installation with Docker

### 1. Clone the repository

```bash
git clone <repository-url>
cd autoparts
```

### 2. Create environment file (optional)

```bash
cp .env.example .env
```

### 3. Build and run with Docker Compose

```bash
docker-compose up --build
```

ລະບົບຈະເຮັດວຽກໃນພາກຫຼັງ ແລະ ຮັນ migrations ອັດຕະໂນມັດ

### 4. Access the application

- **Web Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
  - Username: `admin`
  - Password: `admin123`
- **PostgreSQL Database**: localhost:54320
  - Database: `kauto_db`
  - Username: `postgres`
  - Password: `postgres`
- **Redis**: localhost:6379

### 5. Populate sample data (optional)

```bash
docker-compose exec web python manage.py populate_data
```

## 🔧 Installation without Docker

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

```bash
export DJANGO_ENV=dev
export DB_HOST=localhost
export DB_NAME=kauto_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export REDIS_HOST=localhost
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create superuser

```bash
python manage.py createsuperuser
```

### 6. Collect static files

```bash
python manage.py collectstatic
```

### 7. Run the server

```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## 🎯 Docker Commands

### Start services

```bash
docker-compose up
```

### Start in background

```bash
docker-compose up -d
```

### Stop services

```bash
docker-compose down
```

### View logs

```bash
docker-compose logs -f
```

### View specific service logs

```bash
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

### Rebuild containers

```bash
docker-compose up --build
```

### Run Django management commands

```bash
docker-compose exec web python manage.py <command>
```

Examples:
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Populate data
docker-compose exec web python manage.py populate_data

# Django shell
docker-compose exec web python manage.py shell
```

### Access database

```bash
docker-compose exec db psql -U postgres -d kauto_db
```

### Access Redis CLI

```bash
docker-compose exec redis redis-cli
```

### Connect from external tools

**PostgreSQL** (DBeaver, pgAdmin, etc.):
```
Host: localhost
Port: 54320
Database: kauto_db
Username: postgres
Password: postgres
```

**Redis** (Redis Desktop Manager, RedisInsight, etc.):
```
Host: localhost
Port: 6379
```

## 🌐 WebSocket Real-time Updates

ລະບົບໃຊ້ Django Channels ແລະ WebSocket ສຳລັບການອັບເດດແບບ Real-time:

- **ເວລາຂາຍສິນຄ້າອອກ**: ສະຕັອກຈະອັບເດດທັນທີໃນທຸກໜ້າ
- **ເວລາເພີ່ມສິນຄ້າເຂົ້າ**: ສະຕັອກຈະອັບເດດທັນທີໃນທຸກໜ້າ
- **ການສ້າງສິນຄ້າໃໝ່**: ສິນຄ້າໃໝ່ຈະສະແດງທັນທີ

### WebSocket Endpoint

```
ws://localhost:8000/ws/inventory/
```

### WebSocket Events

- `product_created` - ສິນຄ້າໃໝ່ຖືກສ້າງ
- `product_updated` - ສິນຄ້າຖືກອັບເດດ
- `product_sold` - ສິນຄ້າຖືກຂາຍອອກ
- `stock_added` - ສິນຄ້າຖືກເພີ່ມເຂົ້າ

## 📁 Project Structure

```
autoparts/
├── config/               # Project configuration
│   ├── settings/        # Settings split (base, dev, prod)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── asgi.py          # ASGI configuration
│   ├── urls.py
│   └── wsgi.py
├── store/               # Main app
│   ├── management/      # Management commands
│   │   └── commands/
│   │       └── populate_data.py
│   ├── templates/       # Templates
│   ├── consumers.py     # WebSocket consumers
│   ├── routing.py       # WebSocket routing
│   ├── signals.py       # Django signals for real-time
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── static/              # Static files
│   └── js/
│       ├── language-switcher.js
│       └── websocket-client.js
├── templates/           # Global templates
├── media/               # User uploads
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── requirements.txt     # Python dependencies
├── entrypoint.sh        # Docker entrypoint script
├── .env.example         # Environment variables example
└── manage.py

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_ENV` | Environment (dev/prod) | `dev` |
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | (auto-generated) |
| `ALLOWED_HOSTS` | Allowed hosts | `*` |
| `DB_NAME` | Database name | `kauto_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `db` |
| `DB_PORT` | Database port | `5432` |
| `REDIS_HOST` | Redis host | `redis` |

## 🎨 Features Highlight

### 1. POS System (ລະບົບຂາຍສິນຄ້າ)
- Barcode scanning support
- Real-time inventory updates
- Transaction history

### 2. Inventory Management (ຄຸ້ມຄອງສະຕັອກ)
- Stock in/out tracking
- Low stock alerts
- Product categorization

### 3. Real-time Updates (ອັບເດດແບບ Real-time)
- WebSocket connections
- Automatic UI updates
- Multi-user support

### 4. Multi-language (ຫຼາຍພາສາ)
- Lao (ພາສາລາວ)
- Thai (ภาษาไทย)
- English

### 5. Dark Mode (ໂໝດມືດ)
- Automatic dark mode toggle
- Minimalist black/white design

## 📊 Database Schema

### Models:
- `Brand` - ຍີ່ຫໍ້ສິນຄ້າ
- `Product` - ສິນຄ້າ
- `Transaction` - ປະຫວັດການເຄື່ອນໄຫວ (IN/OUT)

## 🚨 Troubleshooting

### Port already in use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port in docker-compose.yml
ports:
  - "8001:8000"
```

### Database connection error

```bash
# Restart database service
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Redis connection error

```bash
# Restart Redis service
docker-compose restart redis

# Check Redis logs
docker-compose logs redis
```

## 📝 License

MIT License

## 👥 Contributors

- Your Name

## 📞 Support

For support, email admin@kauto.com or create an issue in the repository.
```

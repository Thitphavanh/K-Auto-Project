#!/bin/bash

# Exit on error
set -e

echo "🚀 K-Auto Parts System - Starting..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
    sleep 1
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready (using nc/netcat)
echo "⏳ Waiting for Redis..."
while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/$REDIS_HOST/6379" 2>/dev/null; do
    sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if not exists (optional)
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@kauto.com', 'admin123');
    print('✅ Superuser created successfully');
else:
    print('ℹ️  Superuser already exists');
" || true

# Populate initial data (optional - uncomment if needed)
# echo "📊 Populating initial data..."
# python manage.py populate_data || true

echo "✅ K-Auto Parts System is ready!"

# Start the application
echo "🚀 Starting Daphne ASGI server..."
exec "$@"

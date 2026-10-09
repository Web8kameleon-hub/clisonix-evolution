#!/bin/bash
# Backup script for production server
# Run before any deployment

echo "🔄 Starting production backup..."
BACKUP_DIR="/opt/clisonix-cloud/backups"
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
echo "📦 Backing up PostgreSQL..."
docker exec clisonix-postgres pg_dump \
  -U clisonix -d clisonixdb \
  > $BACKUP_DIR/db-backup-$TIMESTAMP.sql

if [ $? -eq 0 ]; then
  echo "✅ PostgreSQL backup successful"
  gzip $BACKUP_DIR/db-backup-$TIMESTAMP.sql
else
  echo "❌ PostgreSQL backup failed"
  exit 1
fi

# Backup nginx config
echo "📦 Backing up nginx config..."
if [ -f /opt/clisonix-cloud/nginx.conf ]; then
  cp /opt/clisonix-cloud/nginx.conf \
     $BACKUP_DIR/nginx-backup-$TIMESTAMP.conf
  echo "✅ nginx config backed up"
else
  echo "⚠️ nginx config not found"
fi

# Backup docker-compose
echo "📦 Backing up docker-compose..."
if [ -f /opt/clisonix-cloud/docker-compose.yml ]; then
  cp /opt/clisonix-cloud/docker-compose.yml \
     $BACKUP_DIR/docker-compose-backup-$TIMESTAMP.yml
  echo "✅ docker-compose backed up"
fi

# Remove old backups (keep last 7 days)
echo "🧹 Cleaning old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.conf" -mtime +7 -delete
find $BACKUP_DIR -name "*.yml" -mtime +7 -delete

echo ""
echo "✅ Backup completed!"
echo "📁 Backups stored at: $BACKUP_DIR"
ls -lah $BACKUP_DIR/ | tail -5

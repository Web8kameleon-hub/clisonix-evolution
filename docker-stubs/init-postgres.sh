#!/bin/bash
set -e

# Create additional database "clisonix" if not exists
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE clisonix' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'clisonix')\gexec
    GRANT ALL PRIVILEGES ON DATABASE clisonix TO clisonix;
EOSQL

echo "✅ Database 'clisonix' created or already exists"

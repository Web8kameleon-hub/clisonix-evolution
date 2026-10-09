#!/bin/bash
# SQL Optimization via Docker
# Run SQL optimizations inside the PostgreSQL container

echo "============================================================"
echo "🚀 SQL OPTIMIZATION - PostgreSQL Container"
echo "============================================================"

# Connect to postgres container and run optimizations
docker exec clisonix-postgres psql -U postgres -d clisonix -c "

-- Create extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create missing indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_files_user_id ON file_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_files_status ON file_uploads(status);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON file_uploads(uploaded_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_metrics_service ON system_metrics(service);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp DESC);

-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_files_user_status ON file_uploads(user_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_user_status ON jobs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_payments_user_status ON payments(user_id, status);

SELECT 'Indexes created' as status;
" 2>&1

echo ""
echo "🔍 Top 10 Slow Queries:"
docker exec clisonix-postgres psql -U postgres -d clisonix -c "
SELECT 
    query,
    calls,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
ORDER BY mean_time DESC
LIMIT 10;
" 2>&1

echo ""
echo "📊 Analyzing tables..."
docker exec clisonix-postgres psql -U postgres -d clisonix -c "ANALYZE;" 2>&1

echo ""
echo "🧹 Running VACUUM..."
docker exec clisonix-postgres psql -U postgres -d clisonix -c "VACUUM ANALYZE;" 2>&1

echo ""
echo "📈 Table sizes:"
docker exec clisonix-postgres psql -U postgres -d clisonix -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
" 2>&1

echo ""
echo "🔌 Connection stats:"
docker exec clisonix-postgres psql -U postgres -d clisonix -c "
SELECT 
    datname,
    count(*) as connections
FROM pg_stat_activity
GROUP BY datname
ORDER BY connections DESC;
" 2>&1

echo ""
echo "============================================================"
echo "✅ SQL OPTIMIZATION COMPLETE"
echo "============================================================"

#!/usr/bin/env python3
"""
PostgreSQL Connection Pool Tuning Configuration
Provides real-time monitoring and optimization of connection pooling
"""

import psycopg2
from psycopg2 import pool, Error, sql
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple
import os

class PoolTuner:
    """Manages and tunes PostgreSQL connection pooling"""
    
    def __init__(self):
        self.db_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'readme_to_recover'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
        }
        
        # Pool configuration (tunable)
        self.pool_config = {
            'minconn': int(os.getenv('DB_POOL_MIN', 5)),
            'maxconn': int(os.getenv('DB_POOL_MAX', 20)),
        }
        
        self.connection_pool = None
        self.metrics = {
            'total_requests': 0,
            'total_errors': 0,
            'avg_acquisition_time': 0,
            'max_pool_size': self.pool_config['maxconn'],
            'current_size': 0,
            'available_size': 0,
        }
        
    def create_pool(self):
        """Create thread pool for database connections"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                self.pool_config['minconn'],
                self.pool_config['maxconn'],
                **self.db_params
            )
            print(f"✅ Connection pool created: {self.pool_config['minconn']}-{self.pool_config['maxconn']} connections")
            return True
        except Error as e:
            print(f"❌ Error creating connection pool: {e}")
            return False
    
    def get_connection(self, timeout: int = 10):
        """Get connection from pool with timing"""
        start = time.time()
        try:
            conn = self.connection_pool.getconn()
            acquisition_time = (time.time() - start) * 1000  # milliseconds
            self.metrics['total_requests'] += 1
            
            # Update average acquisition time
            avg = self.metrics['avg_acquisition_time']
            count = self.metrics['total_requests']
            self.metrics['avg_acquisition_time'] = (avg * (count - 1) + acquisition_time) / count
            
            return conn, acquisition_time
        except pool.PoolError as e:
            self.metrics['total_errors'] += 1
            print(f"❌ Pool error: {e}")
            return None, None
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if conn and self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, timeout: int = 5):
        """Execute query with pool and timing"""
        conn, acq_time = self.get_connection()
        if not conn:
            return None, None
        
        try:
            cursor = conn.cursor()
            start = time.time()
            cursor.execute(query)
            exec_time = (time.time() - start) * 1000
            
            result = cursor.fetchall()
            cursor.close()
            conn.commit()
            
            return {
                'rows': len(result),
                'acquisition_ms': acq_time,
                'execution_ms': exec_time,
                'total_ms': acq_time + exec_time,
                'success': True
            }, result
        except Error as e:
            self.metrics['total_errors'] += 1
            print(f"❌ Query error: {e}")
            return {'success': False, 'error': str(e)}, None
        finally:
            self.return_connection(conn)
    
    def analyze_pool_stats(self) -> Dict:
        """Analyze current pool statistics from database"""
        query = """
        SELECT 
            datname as database,
            count(*) as total_connections,
            sum(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active,
            sum(CASE WHEN state = 'idle' THEN 1 ELSE 0 END) as idle,
            sum(CASE WHEN state = 'idle in transaction' THEN 1 ELSE 0 END) as idle_in_tx,
            ROUND(AVG(EXTRACT(EPOCH FROM (now() - query_start))), 2) as avg_query_duration_sec,
            MAX(EXTRACT(EPOCH FROM (now() - query_start))) as max_query_duration_sec
        FROM pg_stat_activity
        WHERE datname = %s
        GROUP BY datname;
        """
        
        conn, _ = self.get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (self.db_params['database'],))
            result = cursor.fetchone()
            cursor.close()
            conn.commit()
            
            if result:
                return {
                    'database': result[0],
                    'total_connections': result[1],
                    'active': result[2],
                    'idle': result[3],
                    'idle_in_transaction': result[4],
                    'avg_query_duration_sec': result[5],
                    'max_query_duration_sec': result[6],
                }
            return {}
        except Error as e:
            print(f"❌ Error analyzing pool stats: {e}")
            return {}
        finally:
            self.return_connection(conn)
    
    def get_slow_queries(self, limit: int = 5) -> List[Dict]:
        """Retrieve slowest queries"""
        query = """
        SELECT 
            LEFT(query, 100) as query,
            calls,
            ROUND(mean_time::numeric, 2) as mean_ms,
            ROUND(max_time::numeric, 2) as max_ms,
            ROUND(total_time::numeric, 2) as total_ms
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat_statements%'
        ORDER BY mean_time DESC
        LIMIT %s;
        """
        
        conn, _ = self.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            conn.commit()
            
            slow_queries = []
            for row in results:
                slow_queries.append({
                    'query': row[0],
                    'calls': row[1],
                    'mean_ms': row[2],
                    'max_ms': row[3],
                    'total_ms': row[4],
                })
            return slow_queries
        except Error as e:
            print(f"❌ Error getting slow queries: {e}")
            return []
        finally:
            self.return_connection(conn)
    
    def get_recommended_pool_size(self) -> Dict:
        """Calculate recommended pool size based on system"""
        import multiprocessing
        
        cpu_count = multiprocessing.cpu_count()
        stats = self.analyze_pool_stats()
        
        recommendations = {
            'cpu_cores': cpu_count,
            'recommended_pool_size': (cpu_count * 2) + 4,  # Common formula
            'min_pool': 5,
            'max_pool': (cpu_count * 4),
            'current_pool_min': self.pool_config['minconn'],
            'current_pool_max': self.pool_config['maxconn'],
            'active_connections': stats.get('active', 0),
            'total_connections': stats.get('total_connections', 0),
            'idle_connections': stats.get('idle', 0),
            'utilization_percent': (stats.get('total_connections', 0) / self.pool_config['maxconn'] * 100) if self.pool_config['maxconn'] > 0 else 0,
        }
        
        return recommendations
    
    def optimize_settings(self):
        """Apply optimization settings to PostgreSQL"""
        optimizations = [
            "ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';",
            "ALTER SYSTEM SET statement_timeout = '30s';",
            "ALTER SYSTEM SET lock_timeout = '10s';",
            "ALTER SYSTEM SET max_connections = 100;",
            "ALTER SYSTEM SET shared_buffers = '2GB';",
            "ALTER SYSTEM SET effective_cache_size = '4GB';",
            "ALTER SYSTEM SET work_mem = '256MB';",
        ]
        
        conn, _ = self.get_connection()
        if not conn:
            print("❌ Could not connect to apply optimizations")
            return False
        
        try:
            cursor = conn.cursor()
            for opt in optimizations:
                cursor.execute(opt)
                print(f"✅ Applied: {opt.split('SET ')[1].split(';')[0]}")
            conn.commit()
            cursor.close()
            print("\n⚠️  PostgreSQL restart required for changes to take effect")
            return True
        except Error as e:
            print(f"❌ Error applying optimizations: {e}")
            return False
        finally:
            self.return_connection(conn)
    
    def print_report(self):
        """Print comprehensive pool tuning report"""
        print("\n" + "="*70)
        print("📊 CONNECTION POOL TUNING REPORT")
        print("="*70)
        
        # Pool stats
        print("\n🔌 POOL CONFIGURATION:")
        print(f"   Min connections: {self.pool_config['minconn']}")
        print(f"   Max connections: {self.pool_config['maxconn']}")
        
        # Database stats
        print("\n📈 DATABASE STATISTICS:")
        stats = self.analyze_pool_stats()
        if stats:
            print(f"   Total connections: {stats.get('total_connections', 'N/A')}")
            print(f"   Active queries: {stats.get('active', 'N/A')}")
            print(f"   Idle connections: {stats.get('idle', 'N/A')}")
            print(f"   Idle in transaction: {stats.get('idle_in_transaction', 'N/A')}")
            print(f"   Avg query duration: {stats.get('avg_query_duration_sec', 'N/A')}s")
            print(f"   Max query duration: {stats.get('max_query_duration_sec', 'N/A')}s")
        
        # Performance metrics
        print("\n⚡ PERFORMANCE METRICS:")
        print(f"   Total requests: {self.metrics['total_requests']}")
        print(f"   Total errors: {self.metrics['total_errors']}")
        print(f"   Avg acquisition time: {self.metrics['avg_acquisition_time']:.2f}ms")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        recs = self.get_recommended_pool_size()
        print(f"   CPU cores: {recs['cpu_cores']}")
        print(f"   Recommended pool size: {recs['recommended_pool_size']}")
        print(f"   Current utilization: {recs['utilization_percent']:.1f}%")
        
        if recs['utilization_percent'] > 80:
            print(f"   ⚠️  POOL SATURATION: Consider increasing max_pool from {recs['current_pool_max']}")
        elif recs['utilization_percent'] < 20:
            print(f"   ✅ Pool utilization low - current settings adequate")
        
        # Slow queries
        print("\n🐢 TOP SLOW QUERIES:")
        slow = self.get_slow_queries(3)
        if slow:
            for i, q in enumerate(slow, 1):
                print(f"   {i}. {q['query'][:50]}...")
                print(f"      Mean: {q['mean_ms']}ms | Max: {q['max_ms']}ms | Calls: {q['calls']}")
        
        print("\n" + "="*70)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PostgreSQL Connection Pool Tuner')
    parser.add_argument('--action', choices=['analyze', 'optimize', 'test', 'report'],
                       default='report', help='Action to perform')
    parser.add_argument('--pool-size', type=int, help='Test pool size (min-max format)')
    parser.add_argument('--iterations', type=int, default=10, help='Number of test iterations')
    
    args = parser.parse_args()
    
    tuner = PoolTuner()
    
    # Connect to database
    if not tuner.create_pool():
        return 1
    
    try:
        if args.action == 'analyze':
            print("\n📊 Analyzing connection pool...")
            stats = tuner.analyze_pool_stats()
            print(json.dumps(stats, indent=2))
            
        elif args.action == 'optimize':
            print("\n⚙️  Optimizing PostgreSQL settings...")
            tuner.optimize_settings()
            
        elif args.action == 'test':
            print(f"\n🧪 Running {args.iterations} test iterations...")
            for i in range(args.iterations):
                result, _ = tuner.execute_query("SELECT 1;")
                if result and result.get('success'):
                    print(f"   Iter {i+1}: {result['total_ms']:.2f}ms (acq: {result['acquisition_ms']:.2f}ms)")
                else:
                    print(f"   Iter {i+1}: ❌ Failed")
                time.sleep(0.1)
            
        elif args.action == 'report':
            tuner.print_report()
    
    finally:
        if tuner.connection_pool:
            tuner.connection_pool.closeall()
            print("\n✅ Connection pool closed")


if __name__ == '__main__':
    main()

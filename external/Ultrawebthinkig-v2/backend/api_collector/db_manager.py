"""
UltraWebThinking - Database Manager
SQLite / PostgreSQL storage për API data

Schema:
    apis (id, name, desc, url, source, category, auth, region, timestamp)
"""

import aiosqlite
import hashlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

class DatabaseManager:
    def __init__(self, db_path: str = "../data/apis.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS apis (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    desc TEXT,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT,
                    auth TEXT,
                    region TEXT DEFAULT 'Global',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    layer INTEGER,
                    metadata TEXT
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_url ON apis(url)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_source ON apis(source)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON apis(category)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_layer ON apis(layer)
            """)
            
            await db.commit()
            self.logger.info("✅ Database initialized")
    
    def generate_api_id(self, url: str, name: str = "") -> str:
        """Generate unique ID for API entry"""
        content = f"{url}|{name}".lower().strip()
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def save_api(self, api_data: Dict[str, Any], layer: int) -> bool:
        """Save single API to database"""
        try:
            api_id = self.generate_api_id(api_data.get("url", ""), api_data.get("name", ""))
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO apis 
                    (id, name, desc, url, source, category, auth, region, layer, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    api_id,
                    api_data.get("name", "")[:500],  # Limit length
                    api_data.get("desc", "")[:1000],
                    api_data.get("url", "")[:500],
                    api_data.get("source", "")[:100],
                    api_data.get("category", "")[:100],
                    api_data.get("auth", "")[:50],
                    api_data.get("region", "Global")[:50],
                    layer,
                    json.dumps(api_data.get("metadata", {}))
                ))
                await db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Failed to save API {api_data.get('name', 'Unknown')}: {e}")
            return False
    
    async def save_apis(self, apis: List[Dict[str, Any]], layer: int) -> int:
        """Save multiple APIs to database"""
        saved_count = 0
        
        async with aiosqlite.connect(self.db_path) as db:
            for api_data in apis:
                try:
                    api_id = self.generate_api_id(api_data.get("url", ""), api_data.get("name", ""))
                    
                    await db.execute("""
                        INSERT OR REPLACE INTO apis 
                        (id, name, desc, url, source, category, auth, region, layer, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        api_id,
                        api_data.get("name", "")[:500],
                        api_data.get("desc", "")[:1000],
                        api_data.get("url", "")[:500],
                        api_data.get("source", "")[:100],
                        api_data.get("category", "")[:100],
                        api_data.get("auth", "")[:50],
                        api_data.get("region", "Global")[:50],
                        layer,
                        json.dumps(api_data.get("metadata", {}))
                    ))
                    saved_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to save API {api_data.get('name', 'Unknown')}: {e}")
            
            await db.commit()
        
        self.logger.info(f"💾 Saved {saved_count}/{len(apis)} APIs to database")
        return saved_count
    
    async def get_apis_by_layer(self, layer: int) -> List[Dict[str, Any]]:
        """Get all APIs from specific layer"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM apis WHERE layer = ?", (layer,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_apis_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all APIs from specific category"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM apis WHERE category LIKE ?", (f"%{category}%",))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def search_apis(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search APIs by name or description"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM apis 
                WHERE name LIKE ? OR desc LIKE ? 
                ORDER BY name 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_all_apis(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all APIs from database"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if limit:
                cursor = await db.execute("SELECT * FROM apis ORDER BY timestamp DESC LIMIT ?", (limit,))
            else:
                cursor = await db.execute("SELECT * FROM apis ORDER BY timestamp DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total APIs
            cursor = await db.execute("SELECT COUNT(*) FROM apis")
            total_apis = (await cursor.fetchone())[0]
            
            # Unique URLs
            cursor = await db.execute("SELECT COUNT(DISTINCT url) FROM apis")
            unique_urls = (await cursor.fetchone())[0]
            
            # Categories
            cursor = await db.execute("SELECT COUNT(DISTINCT category) FROM apis WHERE category != ''")
            categories = (await cursor.fetchone())[0]
            
            # Sources
            cursor = await db.execute("SELECT COUNT(DISTINCT source) FROM apis")
            sources = (await cursor.fetchone())[0]
            
            # Layer breakdown
            cursor = await db.execute("SELECT layer, COUNT(*) FROM apis GROUP BY layer ORDER BY layer")
            layer_stats = {f"layer_{row[0]}": row[1] for row in await cursor.fetchall()}
            
            # Top categories
            cursor = await db.execute("""
                SELECT category, COUNT(*) as count 
                FROM apis 
                WHERE category != '' 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_categories = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # Auth types
            cursor = await db.execute("""
                SELECT auth, COUNT(*) as count 
                FROM apis 
                WHERE auth != '' 
                GROUP BY auth 
                ORDER BY count DESC
            """)
            auth_types = {row[0]: row[1] for row in await cursor.fetchall()}
            
            return {
                "total_apis": total_apis,
                "unique_urls": unique_urls,
                "categories": categories,
                "sources": sources,
                "layer_breakdown": layer_stats,
                "top_categories": top_categories,
                "auth_types": auth_types,
                "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
    
    async def deduplicate_by_url(self) -> int:
        """Remove duplicate URLs keeping the most recent entry"""
        async with aiosqlite.connect(self.db_path) as db:
            # Delete duplicates keeping only the latest timestamp for each URL
            await db.execute("""
                DELETE FROM apis 
                WHERE id NOT IN (
                    SELECT id FROM apis a1 
                    WHERE a1.timestamp = (
                        SELECT MAX(a2.timestamp) 
                        FROM apis a2 
                        WHERE a2.url = a1.url
                    )
                )
            """)
            
            deleted_count = db.total_changes
            await db.commit()
            
            self.logger.info(f"🔄 Removed {deleted_count} duplicate URLs")
            return deleted_count
    
    async def cleanup_database(self):
        """Clean up database (remove duplicates, invalid entries)"""
        async with aiosqlite.connect(self.db_path) as db:
            # Remove entries with empty URLs
            await db.execute("DELETE FROM apis WHERE url = '' OR url IS NULL")
            empty_url_count = db.total_changes
            
            # Remove entries with empty names
            await db.execute("DELETE FROM apis WHERE name = '' OR name IS NULL")
            empty_name_count = db.total_changes - empty_url_count
            
            await db.commit()
            
            # Deduplicate by URL
            duplicate_count = await self.deduplicate_by_url()
            
            self.logger.info(f"🧹 Database cleanup completed:")
            self.logger.info(f"   Removed {empty_url_count} entries with empty URLs")
            self.logger.info(f"   Removed {empty_name_count} entries with empty names")
            self.logger.info(f"   Removed {duplicate_count} duplicate URLs")

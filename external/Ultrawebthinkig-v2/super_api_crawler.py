"""
super_api_crawler.py – baza për 200k API crawler
pip install aiohttp aiosqlite tqdm pyyaml
"""
import aiohttp, asyncio, json, hashlib, aiosqlite, yaml
from tqdm import tqdm

DB_PATH = "apis.db"

async def save_api(db, entry):
    key = hashlib.sha1(entry["url"].encode()).hexdigest()
    await db.execute(
        "INSERT OR IGNORE INTO apis (id,name,desc,url,source,auth) VALUES (?,?,?,?,?,?)",
        (key, entry["name"], entry["desc"], entry["url"], entry["source"], entry.get("auth",""))
    )

async def fetch_json(session, url, source):
    try:
        async with session.get(url, timeout=30) as r:
            j = await r.json()
            rows = []
            if "entries" in j:     # publicapis.org style
                for e in j["entries"]:
                    rows.append({"name":e["API"],"desc":e["Description"],
                                 "url":e["Link"],"auth":e["Auth"],"source":source})
            else:
                for k,v in j.items():    # apis.guru style
                    info = v.get("versions",{})
                    rows.append({"name":k,"desc":v.get("info",{}).get("title",""),
                                 "url":v.get("swaggerUrl",k),"auth":"","source":source})
            return rows
    except Exception as e:
        print("err",source,e)
        return []

async def main():
    urls = {
        "publicapis":"https://api.publicapis.org/entries",
        "apisguru":"https://api.apis.guru/v2/list.json"
    }
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS apis(
            id TEXT PRIMARY KEY, name TEXT, desc TEXT, url TEXT, source TEXT, auth TEXT)""")
        async with aiohttp.ClientSession() as session:
            for src,u in urls.items():
                data = await fetch_json(session,u,src)
                for d in tqdm(data,desc=src):
                    await save_api(db,d)
            await db.commit()

if __name__ == "__main__":
    asyncio.run(main())

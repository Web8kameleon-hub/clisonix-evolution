"""
collect_apis.py
Mbledh API nga disa katalogë publikë, i bashkon dhe eksporton në Excel.
Për të filluar:
pip install requests pandas openpyxl

Ekzekuto:
python collect_apis.py

Rezultati: ./open_apis_combined.xlsx
"""

import requests, json, time
import pandas as pd
from urllib.parse import urlparse

OUT_XLSX = "open_apis_combined.xlsx"

def fetch_public_apis_org():
    url = "https://api.publicapis.org/entries"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    j = r.json()
    rows = []
    for e in j.get("entries", []):
        rows.append({
            "source": "publicapis.org",
            "API": e.get("API"),
            "Description": e.get("Description"),
            "Auth": e.get("Auth") or "",
            "HTTPS": e.get("HTTPS"),
            "Cors": e.get("Cors"),
            "Link": e.get("Link"),
            "Category": e.get("Category"),
        })
    return rows

def fetch_apis_guru():
    url = "https://api.apis.guru/v2/list.json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    j = r.json()
    rows = []
    for api_name, api_obj in j.items():
        # take first version available
        versions = list(api_obj.get("versions", {}).items())
        if not versions:
            continue
        ver, verobj = versions[0]
        info = verobj.get("info", {})
        title = info.get("title") or api_name
        description = info.get("description") or ""
        servers = verobj.get("servers", [])
        link = servers[0].get("url") if servers else api_obj.get("swaggerUrl") or api_name
        rows.append({
            "source": "apis.guru",
            "API": title,
            "Description": description,
            "Auth": "",  # not standardized here
            "HTTPS": True,
            "Cors": "",
            "Link": link,
            "Category": api_obj.get("x-google-marketplace-categories") or ""
        })
    return rows

def fetch_github_public_apis_md():
    # raw public-apis repo (README list). We'll parse basic lines (best-effort).
    url = "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    text = r.text
    rows = []
    cat = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            cat = line[3:].strip()
        if line.startswith("- ["):
            # pattern: - [API Name](link) — description
            try:
                left, _, desc = line.partition("—")
                name_part, link_part = left.split("](")
                name = name_part.replace("- [","").replace("[","").strip()
                link = link_part.replace(")","").strip()
                rows.append({
                    "source": "public-apis-md",
                    "API": name,
                    "Description": desc.strip(),
                    "Auth": "",
                    "HTTPS": urlparse(link).scheme == "https",
                    "Cors": "",
                    "Link": link,
                    "Category": cat or ""
                })
            except Exception:
                continue
    return rows

def dedupe_and_normalize(rows):
    df = pd.DataFrame(rows)
    # normalize columns
    for col in ["API","Description","Auth","Link","Category","source","HTTPS","Cors"]:
        if col not in df.columns:
            df[col] = ""
    # drop exact duplicates on Link or API+Category
    df["Link_clean"] = df["Link"].astype(str).str.rstrip("/")
    df = df.sort_values("source")  # prefer apis.guru later in order if duplicates
    df = df.drop_duplicates(subset=["Link_clean"], keep="first")
    df = df.drop(columns=["Link_clean"])
    # basic reorder
    cols = ["API","Description","Category","Auth","HTTPS","Cors","Link","source"]
    df = df[cols]
    df = df.fillna("")
    return df

def main():
    print("Fetching publicapis.org ...")
    rows = []
    try:
        rows += fetch_public_apis_org()
        time.sleep(0.5)
    except Exception as e:
        print("publicapis.org failed:", e)
    print("Fetching apis.guru ...")
    try:
        rows += fetch_apis_guru()
        time.sleep(0.5)
    except Exception as e:
        print("apis.guru failed:", e)
    print("Fetching public-apis README.md ...")
    try:
        rows += fetch_github_public_apis_md()
        time.sleep(0.5)
    except Exception as e:
        print("public-apis md failed:", e)

    print(f"Collected ~{len(rows)} raw entries. Normalizing...")
    df = dedupe_and_normalize(rows)
    print(f"After dedupe: {len(df)} entries. Exporting to Excel: {OUT_XLSX}")
    df.to_excel(OUT_XLSX, index=False)
    print("Done. Open", OUT_XLSX)

if __name__ == "__main__":
    main()

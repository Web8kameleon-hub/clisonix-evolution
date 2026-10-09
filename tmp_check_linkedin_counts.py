import json
import urllib.request

pending = json.load(urllib.request.urlopen("http://127.0.0.1:8007/api/linkedin/pending-articles")).get("count")
posted = json.load(urllib.request.urlopen("http://127.0.0.1:8007/api/linkedin/posted-articles")).get("count")
print(f"pending={pending}")
print(f"posted={posted}")

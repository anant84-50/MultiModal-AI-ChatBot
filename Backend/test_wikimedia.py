import httpx

query = "tiger in jungle"
url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={query}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json&gsrlimit=3"

headers = {"User-Agent": "MultimodalChatbot/1.0 (test@example.com)"}
r = httpx.get(url, headers=headers, timeout=10.0)
print("Wikimedia status:", r.status_code)
if r.status_code == 200:
    pages = r.json().get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        imageinfo = page.get("imageinfo", [{}])[0]
        img_url = imageinfo.get("url")
        print("Found Wikimedia Image:", img_url)

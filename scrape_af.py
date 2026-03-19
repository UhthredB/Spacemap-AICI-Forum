import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

OUT_FILE = Path("af_posts_raw.json")
ENDPOINT = "https://www.alignmentforum.org/graphql"
LIMIT = 50

async def fetch_batch(page, before=None):
    before_clause = (', before:"' + before + '"') if before else ''
    query = "{ posts(input:{ terms:{ view:\"allPosts\", limit:" + str(LIMIT) + before_clause + " } }) { results { _id title slug postedAt baseScore voteCount commentCount wordCount pageUrl user{username} tags{name} contents{plaintextMainText} } } }"
    result = await page.evaluate("""
        async ({url, q}) => {
            const r = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: q })
            });
            return await r.json();
        }
    """, {"url": ENDPOINT, "q": query})
    try:
        return result["data"]["posts"]["results"]
    except:
        print("Batch error:", str(result)[:200])
        return []

async def scrape():
    seen_ids = set()
    posts = []
    if OUT_FILE.exists():
        posts = json.loads(OUT_FILE.read_text())
        seen_ids = {p["_id"] for p in posts}
        print("Resuming: " + str(len(posts)) + " posts already fetched")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Loading AF to pass security checkpoint...")
        await page.goto("https://www.alignmentforum.org", wait_until="networkidle")
        print("Passed checkpoint. Starting cursor-based scrape...")

        # Start cursor: oldest post date we already have, or None for fresh start
        before = None
        if posts:
            oldest = min(posts, key=lambda p: p["postedAt"])
            before = oldest["postedAt"]
            print("Cursor start: " + before)

        empty_streak = 0
        while True:
            batch = await fetch_batch(page, before)
            if not batch:
                empty_streak += 1
                if empty_streak >= 3:
                    break
                continue
            empty_streak = 0
            new_posts = [p for p in batch if p["_id"] not in seen_ids]
            if not new_posts:
                print("No new posts in batch - done.")
                break
            for post in new_posts:
                txt = ""
                if post.get("contents") and post["contents"].get("plaintextMainText"):
                    txt = post["contents"]["plaintextMainText"]
                post["excerpt"] = txt[:600]
                del post["contents"]
                seen_ids.add(post["_id"])
            posts.extend(new_posts)
            before = min(batch, key=lambda p: p["postedAt"])["postedAt"]
            OUT_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False))
            print("  Total: " + str(len(posts)) + " | cursor=" + str(before))

        await browser.close()
    print("\nDone. " + str(len(posts)) + " posts saved to " + str(OUT_FILE))

asyncio.run(scrape())

import json, os, numpy as np, random
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Phase 3 step 1: Loading data...")
posts = json.loads(Path("af_posts_embedded.json").read_text())
embeddings = np.load("af_embeddings.npy")
print("Loaded " + str(len(posts)) + " posts")

print("Phase 3 step 2: Computing edges within clusters...")
clusters = {}
for i, post in enumerate(posts):
    cid = post["cluster_id"]
    if cid not in clusters:
        clusters[cid] = []
    clusters[cid].append(i)

edges = []
seen_pairs = set()
node_degree = {}

for cid, indices in sorted(clusters.items()):
    if len(indices) < 2:
        continue
    ce = embeddings[indices]
    sims = cosine_similarity(ce)
    for li, gi in enumerate(indices):
        if node_degree.get(gi, 0) >= 5:
            continue
        row = sorted([(indices[lj], sims[li][lj]) for lj in range(len(indices)) if lj != li], key=lambda x: x[1], reverse=True)
        for gj, sim in row:
            if sim < 0.65:
                break
            if node_degree.get(gi, 0) >= 5:
                break
            pair = (min(gi, gj), max(gi, gj))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            edges.append({"source_id": posts[gi]["id"], "target_id": posts[gj]["id"], "weight": float(sim), "label": ""})
            node_degree[gi] = node_degree.get(gi, 0) + 1
            node_degree[gj] = node_degree.get(gj, 0) + 1
    print("  Cluster " + str(cid) + ": " + str(len(indices)) + " posts | total edges: " + str(len(edges)))

print("Total edges: " + str(len(edges)))

print("Phase 3 step 3: LLM labeling 150 sample edges...")
post_map = {p["id"]: p for p in posts}
sample_edges = random.sample(edges, min(150, len(edges)))
for i, edge in enumerate(sample_edges):
    src = post_map.get(edge["source_id"], {})
    tgt = post_map.get(edge["target_id"], {})
    prompt = "Post A: " + src.get("title","") + " | Post B: " + tgt.get("title","") + " | In 4-6 words, describe how these two AI alignment posts relate conceptually. Reply with ONLY the label."
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        edge["label"] = r.choices[0].message.content.strip()
    except Exception as ex:
        print("  Error: " + str(ex))
    if (i+1) % 25 == 0:
        print("  Labeled " + str(i+1) + "/150")

print("Saving af_edges.json...")
Path("af_edges.json").write_text(json.dumps(edges, indent=2, ensure_ascii=False))
print("Phase 3 complete!")
print("Edges: " + str(len(edges)))
print("Output: af_edges.json")

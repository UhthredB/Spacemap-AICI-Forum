import json, os, numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import umap
import hdbscan
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

print("Phase 2 step 1: Loading posts...")
posts = json.loads(Path("af_posts_raw.json").read_text())
print("Loaded " + str(len(posts)) + " posts")

print("Phase 2 step 2: Building text inputs...")
texts = []
for p in posts:
    tags = " ".join([t["name"] for t in (p.get("tags") or [])])
    excerpt = (p.get("excerpt") or "")[:400]
    texts.append((p.get("title") or "") + " " + tags + " " + excerpt)

print("Phase 2 step 3: Generating embeddings with all-mpnet-base-v2...")
model = SentenceTransformer("all-mpnet-base-v2")
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
np.save("af_embeddings.npy", embeddings)
print("Embeddings saved: shape " + str(embeddings.shape))

print("Phase 2 step 4: Running UMAP 3D projection...")
reducer = umap.UMAP(n_components=3, metric="cosine", n_neighbors=15, min_dist=0.1, random_state=42)
embeddings_3d = reducer.fit_transform(embeddings)
print("UMAP done. Shape: " + str(embeddings_3d.shape))

print("Phase 2 step 5: Running HDBSCAN clustering...")
clusterer = hdbscan.HDBSCAN(min_cluster_size=15, metric="emclidean", cluster_selection_method="eom")
labels = clusterer.fit_predict(embeddings)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print("Clusters found: " + str(n_clusters))

# Assign noise points to nearest cluster
from sklearn.metrics import pairwise_distances_argmin
if -1 in labels:
    noise_mask = labels == -1
    core_mask = labels != -1
    core_embeddings = embeddings[core_mask]
    core_labels = labels[core_mask]
    noise_embeddings = embeddings[noise_mask]
    nearest = pairwise_distances_argmin(noise_embeddings, core_embeddings)[0]
    labels[noise_mask] = core_labels[nearest]
    print("Noise points reassigned.")

print("Phase 2 step 6: Naming clusters with gpt-4o...")
cluster_posts = {}
for i, label in enumerate(labels):
    key = int(label)
    if key not in cluster_posts:
        cluster_posts[key] = []
    cluster_posts[key].append(i)

cluster_names = {}
for cluster_id, indices in sorted(cluster_posts.items()):
    sample_idx = sorted(indices, key=lambda i: posts[i].get("baseScore") or 0, reverse=True)[:15]
    titles = "\n".join(["- " + (posts[i].get("title") or "") for i in sample_idx])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":"These are post titles from a cluster in AI alignment research. Give this cluster a 2-4 word thematic name that captures its intellectual focus. Reply with ONLY the name, no explanation.\n\nTitles:\n" + titles}],
        max_tokens=20
    )
    name = response.choices[0].message.content.strip()
    cluster_names[cluster_id] = name
    print("  Cluster " + str(cluster_id) + ": " + name + " (" + str(len(indices)) + " posts)")

Path("cluster_names.json").write_text(json.dumps(cluster_names, indent=2))

print("Phase 2 step 7: Building af_posts_embedded.json...")
enriched = []
for i, post in enumerate(posts):
    cid = int(labels[i])
    x, y, z = embeddings_3d[i]
    enriched.append({
        "id": post.get("_id",""),
        "title": post.get("title",""),
        "slug": post.get("slug",""),
        "x": float(x), "y": float(y), "z": float(z), 
        "cluster_id": cid,
        "cluster_label": cluster_names.get(cid, "Cluster " + str(cid)),
        "score": post.get("baseScore") or 0,
        "date": post.get("postedAt",""),
        "tags": [t["name"] for t in (post.get("tags") or [])],
        "author": (post.get("user") or {}).get("username","anon"),
        "url": post.get("pageUrl",""),
        "excerpt": post.get("excerpt","")[:200],
        "wordCount": post.get("wordCount") or 0,
        "commentCount": post.get("commentCount") or 0
    })

Path("af_posts_embedded.json").write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
print("\n---")
print("Phase 2 complete!")
print("Posts: " + str(len(enriched)))
print("Clusters: " + str(n_clusters))
print("Outputs: af_embeddings.npy, af_posts_embedded.json, cluster_names.json")

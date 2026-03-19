"""
Phase 2 Fix: Re-cluster with proper methodology.
- UMAP 768d → 50d (intermediate reduction for clustering, NOT the 3d visual coords)
- HDBSCAN on 50d embeddings with cosine-aware reduction
- Maps new cluster IDs to existing names via centroid proximity 
- Re-exports af_posts_embedded.json
- No API calls required.
"""
import json, numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import euclidean_distances

print("=" * 60)
print("RECLUSTER: Phase 2 Fix (local only, zero API cost)")
print("=" * 60)

# Step 1: Load data
print("\n[1/7] Loading embeddings and posts...")
embeddings = np.load("af_embeddings.npy")
posts_raw = json.loads(Path("af_posts_raw.json").read_text())
old_posts = json.loads(Path("af_posts_embedded.json").read_text())
old_cluster_names_raw = json.loads(Path("cluster_names.json").read_text())
embeddings_3d = np.load("af_embeddings_3d.npy")

# Backup old cluster names before overwriting
old_cluster_names = dict(old_cluster_names_raw)

print(f"  Embeddings: {embeddings.shape}")
print(f"  Posts: {len(posts_raw)}")
print(f"  Old clusters: {len(old_cluster_names)}")

# Step 2: UMAP reduce to 50 dimensions for clustering
print("\n[2/7] UMAP: 768d → 50d for clustering...")
import umap
reducer_50d = umap.UMAP(
    n_components=50,
    metric="cosine",
    n_neighbors=15,
    min_dist=0.0,  # Tighter for clustering
    random_state=42
)
embeddings_50d = reducer_50d.fit_transform(embeddings)
print(f"  Reduced shape: {embeddings_50d.shape}")

# Step 3: Compute old cluster centroids in 50d space
print("\n[3/7] Computing old cluster centroids in 50d space...")
old_labels = np.array([p["cluster_id"] for p in old_posts])
old_centroids = {}
for cid in set(old_labels):
    mask = old_labels == cid
    old_centroids[cid] = embeddings_50d[mask].mean(axis=0)
print(f"  Old centroids computed: {len(old_centroids)}")

# Step 4: Run HDBSCAN on 50d embeddings
print("\n[4/7] Running HDBSCAN on 50d embeddings...")
import hdbscan
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=10,
    min_samples=3,
    metric="euclidean",
    cluster_selection_method="eom"
)
new_labels = clusterer.fit_predict(embeddings_50d)
n_clusters = len(set(new_labels)) - (1 if -1 in new_labels else 0)
n_noise = (new_labels == -1).sum()
print(f"  Clusters found: {n_clusters}")
print(f"  Noise points: {n_noise}")

# Step 5: Assign noise to nearest cluster
print("\n[5/7] Assigning noise points to nearest cluster...")
if n_noise > 0:
    from sklearn.metrics import pairwise_distances_argmin
    noise_mask = new_labels == -1
    core_mask = new_labels != -1
    core_embeddings = embeddings_50d[core_mask]
    core_labels = new_labels[core_mask]
    noise_embeddings = embeddings_50d[noise_mask]
    nearest = pairwise_distances_argmin(noise_embeddings, core_embeddings)
    new_labels[noise_mask] = core_labels[nearest]
    print(f"  Reassigned {n_noise} noise points")
else:
    print("  No noise points to reassign")

# Step 6: Map new cluster IDs to old names via centroid proximity
print("\n[6/7] Mapping new cluster IDs to existing names...")
new_centroids = {}
for cid in set(new_labels):
    mask = new_labels == cid
    new_centroids[cid] = embeddings_50d[mask].mean(axis=0)

old_cids = sorted(old_centroids.keys())
old_centroid_matrix = np.array([old_centroids[c] for c in old_cids])
new_cluster_names = {}
used_old_names = set()

for new_cid in sorted(new_centroids.keys()):
    new_cent = new_centroids[new_cid].reshape(1, -1)
    dists = euclidean_distances(new_cent, old_centroid_matrix)[0]
    sorted_indices = np.argsort(dists)
    for idx in sorted_indices:
        old_cid = old_cids[idx]
        name = old_cluster_names.get(str(old_cid), f"Cluster {old_cid}")
        if name not in used_old_names:
            new_cluster_names[new_cid] = name
            used_old_names.add(name)
            break
    else:
        new_cluster_names[new_cid] = f"Research Area {new_cid}"
    
    count = (new_labels == new_cid).sum()
    print(f"  Cluster {new_cid}: {new_cluster_names[new_cid]} ({count} posts)")

# Step 7: Build new af_posts_embedded.json
print("\n[7/7] Building corrected af_posts_embedded.json...")
enriched = []
for i, post in enumerate(posts_raw):
    cid = int(new_labels[i])
    x, y, z = embeddings_3d[i]
    enriched.append({
        "id": post.get("_id", ""),
        "title": post.get("title", ""),
        "slug": post.get("slug", ""),
        "x": float(x), "y": float(y), "z": float(z),
        "cluster_id": cid,
        "cluster_label": new_cluster_names.get(cid, f"Cluster {cid}"),
        "score": post.get("baseScore") or 0,
        "date": post.get("postedAt", ""),
        "tags": [t["name"] for t in (post.get("tags") or [])],
        "author": (post.get("user") or {}).get("username", "anon"),
        "url": post.get("pageUrl", ""),
        "excerpt": (post.get("excerpt") or "")[:200],
        "wordCount": post.get("wordCount") or 0,
        "commentCount": post.get("commentCount") or 0
    })

Path("af_posts_embedded.json").write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
Path("cluster_names.json").write_text(json.dumps(
    {str(k): v for k, v in new_cluster_names.items()}, indent=2
))
np.save("af_labels.npy", new_labels)

print("\n" + "=" * 60)
print("Phase 2 Fix COMPLETE")
print(f"  Posts: {len(enriched)}")
print(f"  Clusters: {n_clusters}")
print(f"  Outputs: af_posts_embedded.json, cluster_names.json, af_labels.npy")
print("=" * 60)

"""
Phase 3 Fix: Recompute edges with corrected threshold.
- Threshold: 0.75 (was 0.65)
- Top-5 neighbors per node
- Preserves existing edge labels where source/target pairs match
- No API calls required.
"""
import json, numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

print("=" * 60)
print("RECOMPUTE EDGES: Phase 3 Fix (local only, zero API cost)")
print("=" * 60)

# Step 1: Load data
print("\n[1/4] Loading data...")
posts = json.loads(Path("af_posts_embedded.json").read_text())
embeddings = np.load("af_embeddings.npy")

# Load old edges to preserve labels
old_edges = json.loads(Path("af_edges.json").read_text())
old_label_map = {}
for e in old_edges:
    if e.get("label"):
        key = tuple(sorted([e["source_id"], e["target_id"]]))
        old_label_map[key] = e["label"]
print(f"  Posts: {len(posts)}")
print(f"  Old labeled edges to preserve: {len(old_label_map)}")

# Step 2: Group by cluster
print("\n[2/4] Grouping posts by cluster...")
clusters = {}
for i, post in enumerate(posts):
    cid = post["cluster_id"]
    if cid not in clusters:
        clusters[cid] = []
    clusters[cid].append(i)
print(f"  Clusters: {len(clusters)}")

# Step 3: Compute edges
print("\n[3/4] Computing edges (threshold=0.75, top-5 per node)...")
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
        row = sorted(
            [(indices[lj], sims[li][lj]) for lj in range(len(indices)) if lj != li],
            key=lambda x: x[1], reverse=True
        )
        for gj, sim in row:
            if sim < 0.75:  # FIXED: was 0.65
                break
            if node_degree.get(gi, 0) >= 5:
                break
            pair = (min(gi, gj), max(gi, gj))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            
            src_id = posts[gi]["id"]
            tgt_id = posts[gj]["id"]
            label_key = tuple(sorted([src_id, tgt_id]))
            label = old_label_map.get(label_key, "")
            
            edges.append({
                "source_id": src_id,
                "target_id": tgt_id,
                "weight": float(sim),
                "label": label
            })
            node_degree[gi] = node_degree.get(gi, 0) + 1
            node_degree[gj] = node_degree.get(gj, 0) + 1

print(f"  Total edges: {len(edges)}")
preserved = sum(1 for e in edges if e["label"])
print(f"  Preserved labels: {preserved}")

# Step 4: Save
print("\n[4/4] Saving af_edges.json...")
Path("af_edges.json").write_text(json.dumps(edges, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("Phase 3 Fix COMPLETE")
print(f"  Edges: {len(edges)}")
print(f"  Labels preserved: {preserved}")
print(f"  Output: af_edges.json")
print("=" * 60)

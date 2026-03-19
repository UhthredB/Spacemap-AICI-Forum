# AICI Map — User Guide

> **Topologies of Alignment Thought**
> An interactive 3D knowledge graph of 3,900 AI Alignment Forum posts.

---

## Quick Start

```bash
cd "/path/to/AICI Map"
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080) in a modern browser (Chrome/Edge recommended for WebGL2 + bloom).

---

## What You're Looking At

Each **glowing sphere** is a post from the [AI Alignment Forum](https://www.alignmentforum.org). Posts are grouped into **98 research clusters** — each cluster gets a distinct color from a bioluminescent palette (teals, violets, blues, ambers). Larger spheres = higher-scoring posts. The thin **colored lines** connecting spheres are similarity edges — posts whose embeddings are within a 0.75 cosine similarity threshold.

The small **orange dots** flowing along edges are impulse particles — a visual heartbeat showing the connective tissue of the knowledge graph.

---

## Navigation (3D Controls)

| Action | How |
|---|---|
| **Rotate** | Click + drag |
| **Zoom** | Scroll wheel (or pinch) |
| **Pan** | Right-click + drag |
| **Reset view** | Double-click empty space, then zoom out |

The camera has smooth damping — it glides to a stop rather than snapping. Minimum zoom is close enough to read individual nodes; maximum zoom captures the full graph.

---

## The Five Topologies

The bar at the bottom of the screen lets you switch between five different "lenses" on the same data. Each topology rearranges all 3,900 nodes with a smooth 2-second transition.

### 1. Semantic Loom *(default)*
> *"The raw shape of knowledge"*

Nodes are positioned by their semantic embeddings (UMAP 3D reduction). Posts about similar topics are physically close. This is the most faithful representation of how the ideas relate to each other.

**Use when:** You want to explore the natural landscape of alignment research — what topics cluster together, where the dense regions are, and what the outliers look like.

### 2. Gravity Wells
> *"Where does mass concentrate?"*

Nodes are pulled toward their cluster centroids proportional to cluster size. Large clusters become dense gravitational centers; small clusters remain diffuse.

**Use when:** You want to see which research areas have the most concentrated effort. The brightest, densest clusters are where the community has invested the most.

### 3. Archipelago
> *"What are the isolated frontiers?"*

Clusters are exploded apart into separate islands using golden-angle separation. Each cluster becomes its own floating archipelago with clear visual separation.

**Use when:** You want to see the distinct research communities in isolation. This is the best view for counting clusters, comparing their sizes at a glance, and identifying niche research areas.

### 4. Temporal Strata
> *"How did this field grow?"*

The Y-axis (vertical) maps to publication date. Bottom = oldest posts, top = newest. The X and Z axes still preserve the semantic layout.

**Use when:** You want to understand the evolution of alignment research. Watch how topics emerged over time, which areas are recent, and which have deep historical roots.

### 5. Influence Cartography
> *"Who are the gravitational centers?"*

Nodes by prolific/high-scoring authors are pulled toward the center. The most influential researchers' work collapses inward, while occasional contributors remain at the periphery.

**Use when:** You want to identify the key researchers and see how their work spans across topics.

---

## Interacting with Posts

### Hover
Move your mouse over any node to see a **glassmorphism tooltip** showing:
- **Title** of the post
- **Author** name
- **Date** published
- **Score** (upvotes) · comment count · word count
- **Tags** from the Alignment Forum
- **Cluster label** (color-coded badge)

### Click
Click any node to **open the original post** on the Alignment Forum in a new tab.

---

## Search

The search bar at the top center accepts any text query. As you type:
- **Matching posts** (by title, author, or tag) are highlighted in white
- **Non-matching posts** are dimmed to near-invisible
- Clear the search field to restore all posts

**Try searching:** `corrigibility`, `RLHF`, `Eliezer`, `deceptive alignment`, `interpretability`

---

## Filter Panel (Right Side)

### Cluster Filter
A multi-select dropdown listing all 98 clusters with post counts. Hold `Cmd` (Mac) or `Ctrl` (Windows) to select multiple clusters. Only selected clusters' posts will be visible.

### Date Range (From / To)
Two sliders controlling the year range. Drag "Date From" right to hide older posts; drag "Date To" left to hide newer posts.

**Example:** Set From=2020, To=2023 to see only the post-GPT-3 era of alignment research.

### Min Score
Filters out posts below a score threshold. Drag right to show only high-scoring (community-validated) posts.

**Example:** Set to 50+ to see only the most upvoted posts — the "greatest hits" of alignment research.

### Pulse Recent (30d)
Toggle this checkbox to make posts from the last 30 days **pulse/throb** with a breathing animation. Useful for spotting what's new.

---

## Timeline Scrubber

The slider just above the topology bar controls a **chronological cutoff**. Drag it left to "rewind time" — only posts published before the cutoff date appear. The label below shows the current date.

**Use case:** Drag slowly from left to right to watch the alignment research corpus accumulate over time. Combined with Temporal Strata topology, this creates a time-lapse of the field's growth.

---

## Cluster Intelligence Panel (Left Side)

The left sidebar shows all **98 research clusters** sorted by post count (largest first).

### Each cluster entry shows:
- **Cluster name** in brackets (e.g., `[Language Models (LLMs) & GPT]`)
- **Post count** on the right
- **Density bar** — what percentage of all posts belong to this cluster
- **Top 5 authors** — who writes the most in this cluster
- **Sparkline** — an SVG line chart showing posting activity over time (months)

### Click to Isolate
Click any cluster → all other clusters' nodes become invisible, and the camera **smoothly zooms** to that cluster's centroid. Click the same cluster again to **de-isolate** and show everything.

### Filter Clusters
Type in the "Filter clusters..." input at the top to narrow the list by name.

### Collapse / Expand
Click the **◀** arrow to collapse the panel for a wider viewport. A **▶ Clusters** button appears to restore it.

---

## Recommended Exploration Paths

### 1. "What does the field look like?"
1. Start in **Semantic Loom** — orbit around the graph
2. Switch to **Archipelago** to see the distinct islands
3. Hover over nodes in each island to understand what they are

### 2. "What's hot right now?"
1. Enable **Pulse Recent (30d)** in the filter panel
2. Set **Min Score** to 10+
3. Watch which clusters have pulsing nodes

### 3. "How did a specific topic evolve?"
1. Click a cluster in the left panel to isolate it (e.g., `[Interpretability]`)
2. Switch to **Temporal Strata**
3. See the vertical timeline of that topic's posts

### 4. "Who are the central figures?"
1. Switch to **Influence Cartography**
2. The center-most nodes are by the most prolific/high-scoring authors
3. Hover to see author names

### 5. "What connects everything?"
1. Stay in **Semantic Loom** with all posts visible
2. Search for a specific concept (e.g., `mesa-optimization`)
3. See where those highlighted nodes sit relative to the broader graph

---

## Data Summary

| Metric | Value |
|---|---|
| Total posts | 3,900 |
| Similarity edges | 3,410 (threshold ≥ 0.75) |
| Research clusters | 98 |
| Unique authors | 647 |
| Date range | 2009 – 2025 |
| Embedding model | all-MiniLM-L6-v2 (768d) |
| Clustering | UMAP 50d → HDBSCAN |
| Visualization | UMAP 3d → Three.js r160 |

---

## Keyboard & Browser Tips

- **Performance:** If the animation feels sluggish, try closing other tabs or reducing browser zoom to 90%.
- **Screenshots:** Use browser's built-in screenshot (Cmd+Shift+4 on Mac) while in any topology view.
- **Full screen:** Press `F11` or use browser menu for an immersive experience.
- **Share a view:** The map doesn't have URL state, but you can describe a view as: *"Archipelago topology, cluster [Deceptive Alignment] isolated, score ≥ 20"*.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Blank/black screen | Ensure serving via HTTP (`python3 -m http.server`), not `file://` |
| No bloom/glow | Your browser may not support WebGL2. Use Chrome or Edge. |
| Laggy animation | Close other GPU-heavy tabs. Try reducing browser zoom. |
| Nodes too small | Zoom in (scroll wheel). Most nodes are intentionally small to avoid occlusion. |
| Can't find a post | Use the search bar — it matches title, author, and tags. |
| Cluster panel too long | Use the "Filter clusters..." input to narrow the list. |

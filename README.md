<p align="center">
  <img src="https://img.shields.io/badge/posts-3%2C900-ff9500?style=flat-square&labelColor=0a0a0e" />
  <img src="https://img.shields.io/badge/clusters-98-7b5ea7?style=flat-square&labelColor=0a0a0e" />
  <img src="https://img.shields.io/badge/edges-3%2C410-00bcd4?style=flat-square&labelColor=0a0a0e" />
  <img src="https://img.shields.io/badge/authors-647-4caf50?style=flat-square&labelColor=0a0a0e" />
</p>

# Space Map

### Topologies of Alignment Thought

An interactive 3D knowledge graph that maps the entire [AI Alignment Forum](https://www.alignmentforum.org) corpus — 3,900 posts spanning 2009–2025 — into a navigable, living topology. Fly through the landscape of AI safety research. See its shape. Understand its structure.

> *"Reading 4,000 papers is impossible. Looking at a map is instant."*

---

## The Problem

The AI Alignment Forum is one of the most important archives of AI safety thinking on the internet. It contains nearly 4,000 posts from 647 researchers — foundational work on corrigibility, deceptive alignment, interpretability, RLHF, agent foundations, and dozens of other sub-fields.

But it's presented as a **chronological list**. A wall of titles. If you're new, you have no idea where to start, what connects to what, or what the big picture looks like. If you're experienced, you still can't see the *shape* of the field.

**AICI Map turns that list into a galaxy.**

---

## What It Does

Every post becomes a **glowing sphere** in 3D space. Posts about similar ideas cluster together — not by tags or categories, but by what they actually *mean* (via sentence embeddings). The result is an organic, emergent topology where:

- **98 research clusters** self-organize from the embeddings
- **3,410 similarity edges** connect posts that share deep conceptual overlap
- **5 switchable topology views** let you see the data through different lenses
- **Orange impulse particles** flow along edges like neural signals

You can hover to read, click to visit, search to filter, and isolate entire research areas with one click.

---

## The Five Topologies

| View | Question it answers |
|---|---|
| **Semantic Loom** | What does the raw shape of this knowledge look like? |
| **Gravity Wells** | Where does research mass concentrate? |
| **Archipelago** | What are the isolated frontier islands? |
| **Temporal Strata** | How did this field grow over time? |
| **Influence Cartography** | Who are the gravitational centers? |

Each topology rearranges all 3,900 nodes with a smooth 2-second GSAP transition. Same data, different lens.

---

## The Pipeline

This project was built in six phases:

### Phase 1 — Scraping
`scrape_af.py` pulls post metadata from the Alignment Forum GraphQL API: titles, authors, dates, scores, tags, excerpts, word counts, comment counts. **3,900 posts** collected.

### Phase 2 — Embedding & Clustering
`embed_cluster.py` generates 768-dimensional sentence embeddings using `all-MiniLM-L6-v2` (local, no API calls). UMAP reduces to 50 dimensions for clustering, then HDBSCAN identifies **98 natural clusters**. A separate 3D UMAP reduction provides the spatial coordinates for visualization.

`recluster.py` was a correction pass — the original pipeline mistakenly clustered on 3D coordinates instead of the full embedding space. The fix clusters on UMAP-50d embeddings, producing analytically accurate boundaries.

### Phase 3 — Edge Computation
`recompute_edges.py` computes pairwise cosine similarity on the full 768d embeddings and keeps edges above a **0.75 threshold** — yielding **3,410 edges**. Each edge connects posts that genuinely share ideas, not just surface keywords.

`name_clusters.py` generates human-readable cluster names from the top tags and titles in each group — entirely local, no API costs.

### Phase 4 — 3D Visualization
`index.html` — a single-file Three.js application:
- **InstancedMesh** renders 3,900 spheres with bioluminescent cluster colors
- **UnrealBloomPass** (strength 1.2, radius 0.4, threshold 0.1) creates the glow
- **Star-field particles** fill the background
- **GSAP** animates topology transitions
- **Glassmorphism UI** for tooltips, panels, and controls

### Phase 5 — Cluster Intelligence Panel
A left sidebar panel showing all 98 clusters with:
- Post counts and density bars
- Top 5 authors per cluster
- SVG temporal sparklines (posts/month over time)
- Click-to-isolate with camera zoom to cluster centroid

### Phase 6 — Verification
18-point end-to-end test suite covering every feature: rendering, bloom, topologies, search, filters, tooltips, cluster isolation, and console health. All passed.

---

## Inspiration

The visual aesthetic draws from two sources:

1. **Bioluminescent deep-sea organisms** — the color palette (deep teals, violets, electric blues, warm ambers) and the bloom glow are inspired by creatures that produce their own light in darkness. The metaphor felt right: these are ideas illuminating the dark problem of AI alignment.

2. **[Topologies of Thoughts](https://x.com/)** — a reference visualization of Twitter/X conversations as 3D topology maps. The concept of "topology as interface" — where the *shape* of data is the primary UX — directly inspired the five switchable views.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/UhthredB/Spacemap-AISI-Forum.git
cd Spacemap-AISI-Forum

# Serve locally (any static server works)
python3 -m http.server 8080

# Open in browser
open http://localhost:8080
```

No build step. No npm install. No API keys. Just serve and open.

---

## Project Structure

```
├── index.html                  # The entire visualization (single file)
├── GUIDE.md                    # Detailed user guide
├── af_posts_embedded.json      # 3,900 posts with 3D coords + clusters
├── af_edges.json               # 3,410 similarity edges
├── cluster_names.json          # Human-readable cluster labels
├── lib/                        # Three.js r160 + GSAP (local ES modules)
│   ├── three.module.js
│   ├── gsap.min.js
│   ├── controls/OrbitControls.js
│   ├── postprocessing/         # Bloom pipeline
│   └── shaders/                # Bloom shaders
├── scrape_af.py                # Phase 1: Scrape Alignment Forum
├── embed_cluster.py            # Phase 2: Embed + cluster
├── recluster.py                # Phase 2 fix: Re-cluster on full embeddings
├── generate_edges.py           # Phase 3: Original edge generation
├── recompute_edges.py          # Phase 3 fix: Recompute at 0.75 threshold
└── name_clusters.py            # Cluster naming (local, no API)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Embeddings | `all-MiniLM-L6-v2` via `sentence-transformers` |
| Dimensionality reduction | UMAP (50d for clustering, 3d for viz) |
| Clustering | HDBSCAN |
| Similarity | Cosine similarity on 768d embeddings |
| 3D rendering | Three.js r160 (ES modules, local) |
| Post-processing | UnrealBloomPass |
| Animations | GSAP |
| Data format | JSON (no database) |
| Serving | Any static HTTP server |

---

## Features at a Glance

- 🔮 **3,900 nodes** with bioluminescent cluster colors and bloom glow
- 🕸️ **3,410 edges** with orange impulse particles flowing along them
- 🔄 **5 topology views** with smooth 2s transitions
- 🔍 **Search** with highlight/dim across titles, authors, and tags
- 📊 **Cluster Intelligence Panel** with sparklines, density, top authors
- 🎯 **Click-to-isolate** any cluster with camera zoom
- 📅 **Timeline scrubber** to watch the field grow chronologically
- 🎛️ **Filters** for cluster, date range, and minimum score
- 💡 **"wtf" button** — an ELI5 explainer modal for first-time visitors
- ⚡ **Zero dependencies** to run — just `python3 -m http.server`

---

## Data Notes

- All data was scraped from the public Alignment Forum API
- Embeddings were generated **locally** using `sentence-transformers` (no OpenAI API)
- Cluster names were generated **locally** from top tags and titles (no LLM API)
- The `.npy` embedding files (~16MB) are gitignored — only the processed JSONs are in the repo
- Edge threshold of 0.75 cosine similarity was chosen to balance signal (meaningful connections) with density (not overwhelming the graph)

---

## License

MIT

---

</p>

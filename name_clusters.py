import json, os, numpy as np
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
posts = json.loads(Path('af_posts_raw.json').read_text())
embeddings_3d = np.load('af_embeddings_3d.npy')
labels = np.load('af_labels.npy')

cluster_posts = {}
for i, label in enumerate(labels):
    k = int(label)
    if k not in cluster_posts:
        cluster_posts[k] = []
    cluster_posts[k].append(i)

print('Naming ' + str(len(cluster_posts)) + ' clusters with gpt-4o-mini...')
cluster_names = {}
for cid, indices in sorted(cluster_posts.items()):
    sample = sorted(indices, key=lambda i: posts[i].get('baseScore') or 0, reverse=True)[:15]
    titles = '\n'.join(['- ' + (posts[i].get('title') or '') for i in sample])
    try:
        r = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role':'user','content':'These are AI alignment research post titles from one thematic cluster. Give it a 2-4 word name capturing its intellectual focus. Reply with ONLY the name.\n\n' + titles}],
            max_tokens=20
        )
        name = r.choices[0].message.content.strip()
    except Exception as e:
        name = 'Cluster ' + str(cmd)
        print('  Error: ' + str(e))
    cluster_names[cid] = name
    print('  ' + str(cid) + ': ' + name + ' (' + str(len(indices)) + ' posts)')

Path('cluster_names.json').write_text(json.dumps(cluster_names, indent=2))
print('Cluster names saved.')

print('Building af_posts_embedded.json...')
enriched = []
for i, post in enumerate(posts):
    cid = int(labels[i])
    x, y, z = embeddings_3d[i]
    enriched.append({
        'id': post.get('_id',''),
        'title': post.get('title',''),
        'slug': post.get('slug',''),
        'x': float(x), 'y': float(y), 'z': float(z), 
        'cluster_id': cid,
        'cluster_label': cluster_names.get(cid, 'Cluster ' + str(cid)),
        'score': post.get('baseScore') or 0,
        'date': post.get('postedAt',''),
        'tags': [t['name'] for t in (post.get('tags') or [])],
        'author': (post.get('user') or {}).get('username','anon'),
        'url': post.get('pageUrl',''),
        'excerpt': (post.get('excerpt') or '')[:200],
        'wordCount': post.get('wordCount') or 0,
        'commentCount': post.get('commentCount') or 0
    })

Path('af_posts_embedded.json').write_text(json.dumps(enriched, indent=2, ensure_ascii=False))
print('\nPhase 2 complete!')
print('Posts: ' + str(len(enriched)))
print('Clusters: 90')
print('Outputs: af_posts_embedded.json, cluster_names.json')

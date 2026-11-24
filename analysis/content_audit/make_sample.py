"""Pre-registered sample for the content audit (fixed before any grading).
Population: present question-trace pairs x 2 wordings (148 answers per system).
Sample: 60 (pair, wording) items, stratified by category in proportion to present pairs,
wordings alternated within each category, seed 20261124. The same items are graded for
TraceAssist (run 1) and Codex (run 1), whatever their verdict."""
import json, random, collections, hashlib, sys
R = sys.argv[1]  # repo/bench
key = json.load(open(f'{R}/answer_key.json'))['pairs']
present = [p for p in key if p['truth'] == 'present']
rng = random.Random(20261124)
bycat = collections.defaultdict(list)
for p in present: bycat[p['category']].append(p)
N = 60; total = len(present)*2
quota = {c: round(N*len(v)*2/total) for c, v in bycat.items()}
while sum(quota.values()) != N:
    c = max(quota, key=lambda c: len(bycat[c])); quota[c] += 1 if sum(quota.values()) < N else -1
items = []
for c in sorted(bycat):
    pairs = sorted(bycat[c], key=lambda p: (p['question'], p['run_id'])); rng.shuffle(pairs)
    cand = [(p, w) for p in pairs for w in ('a', 'b')]
    rng.shuffle(cand)
    chosen, seen = [], collections.Counter()
    for p, w in cand:  # balance wordings
        if len(chosen) >= quota[c]: break
        if seen[w] >= (quota[c]+1)//2: continue
        chosen.append((p, w)); seen[w] += 1
    items += [{'item': f"{p['question']}{w}__{p['run_id']}", 'question': p['question'], 'wording': w,
               'run_id': p['run_id'], 'category': c, 'symptom': p['symptom']} for p, w in chosen]
json.dump({'seed': 20261124, 'quota': quota, 'items': items}, open('sample.json', 'w'), indent=1)
print(quota, len(items), collections.Counter(i['wording'] for i in items))
print('sha256', hashlib.sha256(open('sample.json','rb').read()).hexdigest())

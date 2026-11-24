import json, random, sys
R = sys.argv[1]
key = {f"{p['question']}__{p['run_id']}": p for p in json.load(open(f'{R}/answer_key.json'))['pairs']}
qs = {q['id']: q for q in json.load(open(f'{R}/questions.json'))['questions']}
items = json.load(open('sample.json'))['items']
rng = random.Random(7); mapping = {}; out = []
for it in items:
    k = key[f"{it['question']}__{it['run_id']}"]
    ans = {}
    for s in ('traceassist', 'codex'):
        ans[s] = json.load(open(f"{R}/results/{s}/run1/{it['item']}.json"))['answer']
    labels = ['A', 'B']; rng.shuffle(labels)
    mapping[it['item']] = {'traceassist': labels[0], 'codex': labels[1]}
    out.append({'item': it['item'], 'category': it['category'],
                'question': k['wordings'][it['wording']], 'fault_summary': k['fault_summary'],
                'expected': k['expected'],
                'answers': {labels[0]: ans['traceassist'], labels[1]: ans['codex']}})
out.sort(key=lambda x: x['item'])
for i in range(0, len(out), 20):
    json.dump(out[i:i+20], open(f'packets/batch{i//20+1}.json', 'w'), indent=1)
json.dump(mapping, open('blind_mapping.json', 'w'), indent=1)
print(len(out), 'items;', sum(len(json.dumps(o)) for o in out)//1000, 'KB')

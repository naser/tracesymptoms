import json, collections, csv
m = json.load(open('blind_mapping.json'))
G = {g: {x['item']: x for x in json.load(open(f'grades_{g}.json'))} for g in ('codex','claude')}
items = sorted(m)
def get(g, it, sysname): return G[g][it][m[it][sysname]]
def kappa(a, b):
    n=len(a); cats=set(a)|set(b); po=sum(x==y for x,y in zip(a,b))/n
    pe=sum((a.count(c)/n)*(b.count(c)/n) for c in cats); return (po-pe)/(1-pe) if pe<1 else 1
out=[]
for s in ('traceassist','codex'):
    for g in ('codex','claude'):
        c=collections.Counter(get(g,i,s)['overall'] for i in items)
        loc=collections.Counter(get(g,i,s)['location'] for i in items)
        out.append(f"{s:11s} grader={g:6s} overall {dict(c)} location {dict(loc)}")
    a=[get('codex',i,s)['overall'] for i in items]; b=[get('claude',i,s)['overall'] for i in items]
    out.append(f"{s}: overall agreement {sum(x==y for x,y in zip(a,b))}/60, kappa {kappa(a,b):.2f}")
# consensus where graders agree
for s in ('traceassist','codex'):
    agree=[i for i in items if get('codex',i,s)['overall']==get('claude',i,s)['overall']]
    c=collections.Counter(get('codex',i,s)['overall'] for i in agree)
    out.append(f"{s}: consensus on {len(agree)} items: {dict(c)}")
# among each system's 'yes' answers
for s in ('traceassist','codex'):
    yes=[i for i in items if get('codex',i,s)['verdict'].lower().startswith('yes')]
    out.append(f"{s}: yes-verdicts per codex grader {len(yes)}; full by codex-grader {sum(get('codex',i,s)['overall']=='full' for i in yes)}, by claude-grader {sum(get('claude',i,s)['overall']=='full' for i in yes)}")
print('\n'.join(out)); open('results.txt','w').write('\n'.join(out))
with open('disagreements.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['item','system','codex_grader','claude_grader','codex_note','claude_note'])
    for s in ('traceassist','codex'):
        for i in items:
            a=get('codex',i,s); b=get('claude',i,s)
            if a['overall']!=b['overall']: w.writerow([i,s,a['overall'],b['overall'],a.get('note',''),b.get('note','')])

import json, collections
m=json.load(open('blind_mapping.json'))
G={g:{x['item']:x for x in json.load(open(f'grades_{g}.json'))} for g in ('codex','claude')}
adj={x['case']:x for x in json.load(open('adjudicated.json'))}
res={}
for s in ('traceassist','codex'):
    fin=collections.Counter(); yes=collections.Counter(); loc=collections.Counter(); src=collections.Counter()
    by_cat=collections.defaultdict(collections.Counter)
    sample={x['item']:x for x in json.load(open('sample.json'))['items']}
    for it in m:
        L=m[it][s]; a=G['codex'][it][L]; b=G['claude'][it][L]
        if a['overall']==b['overall']: o=a['overall']; src['agreed']+=1
        else: o=adj[f'{it}::{L}']['overall']; src[adj[f'{it}::{L}']['agrees_with']]+=1
        fin[o]+=1; by_cat[sample[it]['category']][o]+=1
        if a['location']==b['location']: loc[a['location']]+=1
        else: loc['disputed']+=1
        if a['verdict'].lower().startswith('yes'): yes[o]+=1
    res[s]={'final':dict(fin),'final_among_yes':dict(yes),'location_agreed':dict(loc),'sources':dict(src),'by_category':{k:dict(v) for k,v in by_cat.items()}}
json.dump(res,open('final_results.json','w'),indent=1); print(json.dumps(res,indent=1))

import csv, random, collections, sys
R = sys.argv[1]
S = ['llm_only','rag','tmll','codex','traceassist']
rows = {s: [r for r in csv.DictReader(open(f'{R}/results/{s}/run1_scores.csv')) if r['truth'] in ('present','absent')] for s in S}
def ba(rs):
    P=[r for r in rs if r['truth']=='present']; A=[r for r in rs if r['truth']=='absent']
    tp=sum(r['outcome']=='TP' for r in P); tn=sum(r['outcome'] in ('TN','TN_abstain') for r in A)
    return (tp/len(P)+tn/len(A))/2 if P and A else float('nan')
def strict_spec(rs):
    A=[r for r in rs if r['truth']=='absent']; return sum(r['outcome']=='TN' for r in A)/len(A)
print('system  BA  strictSpec(no only)  BA_strict  BA_no_batch_server  BA_precise')
for s in S:
    rs=rows[s]; P=[r for r in rs if r['truth']=='present']; A=[r for r in rs if r['truth']=='absent']
    tp=sum(r['outcome']=='TP' for r in P)/len(P)
    nb=[r for r in rs if not r['run_id'].startswith('batch_server')]
    pr=[r for r in rs if r['wording']=='a']
    print(f"{s:12s} {ba(rs):.3f} {strict_spec(rs):.3f} {(tp+strict_spec(rs))/2:.3f} {ba(nb):.3f} {ba(pr):.3f}")
# cluster bootstrap over questions
qs=sorted(set(r['question'] for r in rows['traceassist']))
byq={s: collections.defaultdict(list) for s in S}
for s in S:
    for r in rows[s]: byq[s][r['question']].append(r)
rng=random.Random(1); B=5000; res={s:[] for s in S}; diff=[]
for _ in range(B):
    smp=[rng.choice(qs) for _ in qs]
    v={s: ba([r for q in smp for r in byq[s][q]]) for s in S}
    for s in S: res[s].append(v[s])
    diff.append(v['traceassist']-v['codex'])
def ci(x): x=sorted(x); return x[int(.025*len(x))], x[int(.975*len(x))]
for s in S: print(s, 'BA 95%% CI (cluster bootstrap by question): %.2f-%.2f' % ci(res[s]))
print('TraceAssist - Codex BA diff 95%% CI: %.3f-%.3f' % ci(diff))
# false alarms by pair and McNemar on absent answers (paired by id)
ta={r['id']:r for r in rows['traceassist']}; cx={r['id']:r for r in rows['codex']}
b=sum(1 for i in ta if ta[i]['truth']=='absent' and ta[i]['outcome']=='FP' and cx[i]['outcome']!='FP')
c=sum(1 for i in ta if ta[i]['truth']=='absent' and ta[i]['outcome']!='FP' and cx[i]['outcome']=='FP')
print('paired absent answers: TA-only FP', b, 'Codex-only FP', c)

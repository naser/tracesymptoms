"""Build FP classification CSVs, cross-tabs and effort stats from the manual labels.
Run: python3 build.py  (reads the repo read-only; writes only into this folder)."""
import csv, json, statistics, sys, importlib.util
from collections import Counter, defaultdict
import os
R = os.environ.get('TRACEASSIST_REPO', '../../../traceassist-icpe2027') + '/bench'
HERE = os.path.dirname(os.path.abspath(__file__))
CATS = ['SCALE', 'THRESHOLD', 'INTERPRETATION', 'ADJACENT', 'LITERAL_TRUE', 'WRONG_ENTITY', 'MISMEASURED', 'OTHER']

def load_labels(name):
    spec = importlib.util.spec_from_file_location(name, f'{HERE}/{name}.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m.L

def rows(system):
    return list(csv.DictReader(open(f'{R}/results/{system}/run1_scores.csv')))

out = []
def p(*a): out.append(' '.join(str(x) for x in a))

scores = {s: {r['id']: r for r in rows(s)} for s in ('codex', 'traceassist')}
per_sys = {}
for system, lab in (('codex', 'labels_codex'), ('traceassist', 'labels_traceassist')):
    L = load_labels(lab)
    fps = [r for r in scores[system].values() if r['outcome'] == 'FP']
    assert set(L) == {r['id'] for r in fps}, (system, set(L) ^ {r['id'] for r in fps})
    recs = []
    for r in sorted(fps, key=lambda r: r['id']):
        ans = json.load(open(f'{R}/results/{system}/run1/{r["id"]}.json'))['answer']
        cat, sc, ld, why, quote = L[r['id']]
        assert cat in CATS, cat
        assert quote in ans, (r['id'], quote)
        assert len(quote.split()) <= 20, (r['id'], len(quote.split()))
        assert len(why.split()) <= 25, (r['id'], len(why.split()))
        other = 'traceassist' if system == 'codex' else 'codex'
        recs.append(dict(id=r['id'], question=r['question'], wording=r['wording'], symptom=r['symptom'],
                         group=r['group'], fault=r['fault'], category=cat, self_contradicting=sc,
                         label_debatable=ld, justification=why, quote=quote,
                         other_system_outcome=scores[other][r['id']]['outcome']))
    fn = 'codex_fp_classified.csv' if system == 'codex' else 'traceassist_fp_classified.csv'
    with open(f'{HERE}/{fn}', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0])); w.writeheader(); w.writerows(recs)
    per_sys[system] = recs

def tab(recs, key, title):
    vals = sorted({r[key] for r in recs})
    p(f'\n{title}')
    p('| category | ' + ' | '.join(vals) + ' | total |')
    p('|---|' + '---:|' * (len(vals) + 1))
    for c in CATS:
        n = [sum(1 for r in recs if r['category'] == c and r[key] == v) for v in vals]
        if sum(n): p(f'| {c} | ' + ' | '.join(map(str, n)) + f' | {sum(n)} |')
    p('| total | ' + ' | '.join(str(sum(1 for r in recs if r[key] == v)) for v in vals) + f' | {len(recs)} |')

for system, recs in per_sys.items():
    p(f'\n## {system}: {len(recs)} FPs')
    c = Counter(r['category'] for r in recs)
    p('| category | n | % | self-contradicting | label-debatable |')
    p('|---|---:|---:|---:|---:|')
    for k in CATS:
        if c[k]:
            p(f"| {k} | {c[k]} | {100*c[k]/len(recs):.0f}% | {sum(r['self_contradicting'] for r in recs if r['category']==k)} | {sum(r['label_debatable'] for r in recs if r['category']==k)} |")
    p(f"| all | {len(recs)} | 100% | {sum(r['self_contradicting'] for r in recs)} | {sum(r['label_debatable'] for r in recs)} |")
    tab(recs, 'wording', f'{system}: category x wording (a=precise, b=everyday)')
    tab(recs, 'group', f'{system}: category x symptom group')
    tab(recs, 'fault', f'{system}: category x fault==none') if False else None
    healthy = Counter((r['category'], r['fault'] == 'none') for r in recs)
    p(f'\n{system}: FPs on healthy (fault none) traces: ' + ', '.join(f"{k}={healthy[(k, True)]}" for k in CATS if healthy[(k, True)]) + f" (total {sum(1 for r in recs if r['fault']=='none')})")

# overlap
cx = per_sys['codex']
p('\n## Overlap (same question, wording and trace)')
p('Codex FP -> TraceAssist outcome:', dict(Counter(r['other_system_outcome'] for r in cx)))
p('By Codex category, TraceAssist TN count:')
for k in CATS:
    n = [r for r in cx if r['category'] == k]
    if n: p(f'  {k}: {sum(1 for r in n if r["other_system_outcome"] in ("TN","TN_abstain"))}/{len(n)} TraceAssist TN or TN_abstain; strict TN {sum(1 for r in n if r["other_system_outcome"]=="TN")}')
p('TraceAssist FP -> Codex outcome:', dict(Counter(r['other_system_outcome'] for r in per_sys['traceassist'])))

# effort: TP vs FP
p('\n## Codex effort, TP vs FP (medians)')
def eff(ids):
    nc, el, tok = [], [], []
    for i in ids:
        a = json.load(open(f'{R}/results/codex/run1/{i}.json'))
        nc.append(a.get('n_commands') or 0); el.append(a.get('elapsed_s') or 0)
        u = a.get('usage') or {}; tok.append(u.get('output_tokens') or 0)
    return len(ids), statistics.median(nc), statistics.median(el), statistics.median(tok)
groups = defaultdict(list)
for r in scores['codex'].values(): groups[r['outcome']].append(r['id'])
p('| outcome | n | median n_commands | median elapsed_s | median output_tokens |')
p('|---|---:|---:|---:|---:|')
for o in ('TP', 'FP', 'TN', 'FN'):
    n, a, b, t = eff(groups[o]); p(f'| {o} | {n} | {a} | {b:.0f} | {t} |')
for k in CATS:
    ids = [r['id'] for r in cx if r['category'] == k]
    if ids:
        n, a, b, t = eff(ids); p(f'| FP:{k} | {n} | {a} | {b:.0f} | {t} |')
# within same questions: FP vs TP on same question id (wording-specific)
qs = {r['question'] + r['wording'] for r in cx}
tp_same = [r['id'] for r in scores['codex'].values() if r['outcome'] == 'TP' and r['question'] + r['wording'] in qs]
fp_same = [r['id'] for r in cx]
n, a, b, t = eff(tp_same); p(f'| TP on question-wordings that also have an FP | {n} | {a} | {b:.0f} | {t} |')
# Mann-Whitney without scipy dependency if available
try:
    from scipy.stats import mannwhitneyu
    def vals(ids, k): return [json.load(open(f'{R}/results/codex/run1/{i}.json')).get(k) or 0 for i in ids]
    for k in ('n_commands', 'elapsed_s'):
        p(f'Mann-Whitney TP vs FP on {k}: p = {mannwhitneyu(vals(groups["TP"], k), vals(groups["FP"], k)).pvalue:.3g}')
except ImportError:
    p('(scipy not available: no test)')

# recall/fp context
for s in ('codex', 'traceassist'):
    c = Counter(r['outcome'] for r in scores[s].values()); p(f'{s} outcomes: {dict(c)}')
open(f'{HERE}/counts.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))

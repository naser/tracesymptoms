"""Dump FP answers with question text, symptom criterion and trace fault summary for manual classification."""
import json, csv, sys
import os
R = os.environ.get('TRACEASSIST_REPO', '../../../traceassist-icpe2027') + '/bench'
system = sys.argv[1]
q = {x['id']: x for x in json.load(open(f'{R}/questions.json'))['questions']}
s = {x['id']: x for x in json.load(open(f'{R}/symptoms.json'))['symptoms']}
ak = {(p['question'], p['run_id']): p for p in json.load(open(f'{R}/answer_key.json'))['pairs']}
rows = [x for x in csv.DictReader(open(f'{R}/results/{system}/run1_scores.csv')) if x['outcome'] in ('FP', 'FP_unseeable')]
for i, x in enumerate(rows):
    a = json.load(open(f'{R}/results/{system}/run1/{x["id"]}.json'))
    qid = x['question'] + x['wording']
    k = ak.get((x['question'], x['run_id']), {})
    print(f'=== [{i}] {x["id"]} | {x["symptom"]} | {x["group"]} | wording {x["wording"]} | fault {x["fault"]} | {x["outcome"]}')
    print('CRIT:', s[x['symptom']]['criterion'])
    print('FAULT:', k.get('fault_summary', ''))
    print('Q:', q[qid]['text'])
    print('A:', a['answer'].strip())
    print()

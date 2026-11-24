# TraceSymptoms composition

Counts are computed from unique questions and exported items. The wording table describes one system/run (516 answers), not the seven runs combined.

## Category by hub (unique questions)

| category | single | multi | Total |
| --- | --- | --- | --- |
| comprehension | 8 | 3 | 11 |
| dependency | 4 | 6 | 10 |
| quantitative | 8 | 6 | 14 |
| remediation | 4 | 3 | 7 |
| root_cause | 2 | 12 | 14 |
| Total | 26 | 30 | 56 |

## Symptom group by truth (pairs)

| symptom_group | present | absent | cannot_see | Total |
| --- | --- | --- | --- | --- |
| cpu | 19 | 42 | 2 | 63 |
| lifecycle | 4 | 15 | 1 | 20 |
| pipelines | 4 | 14 | 0 | 18 |
| syscalls_io | 7 | 20 | 3 | 30 |
| timing | 7 | 24 | 0 | 31 |
| unexpected | 6 | 14 | 0 | 20 |
| waiting | 27 | 49 | 0 | 76 |
| Total | 74 | 178 | 6 | 258 |

## Program by truth (pairs)

| program | present | absent | cannot_see | Total |
| --- | --- | --- | --- | --- |
| batch_server | 16 | 27 | 0 | 43 |
| cachesvc | 1 | 2 | 3 | 6 |
| crunch | 16 | 32 | 2 | 50 |
| filestore | 9 | 25 | 0 | 34 |
| jobrunner | 6 | 23 | 1 | 30 |
| kvstore | 7 | 13 | 0 | 20 |
| pipeline | 7 | 26 | 0 | 33 |
| reporter | 3 | 5 | 0 | 8 |
| ticker | 9 | 25 | 0 | 34 |
| Total | 74 | 178 | 6 | 258 |

## Wording by truth (answers per system/run)

| wording | present | absent | cannot_see | Total |
| --- | --- | --- | --- | --- |
| a (precise) | 74 | 178 | 6 | 258 |
| b (everyday) | 74 | 178 | 6 | 258 |
| Total | 148 | 356 | 12 | 516 |

# TraceSymptoms checks

PASS: 64 of 64 checks passed.

## Required composition

| Check | Actual | Expected | Status |
| --- | --- | --- | --- |
| Questions | 56 | 56 | PASS |
| Wordings | 112 | 112 | PASS |
| Pairs | 258 | 258 | PASS |
| Pairs: present | 74 | 74 | PASS |
| Pairs: absent | 178 | 178 | PASS |
| Pairs: cannot_see | 6 | 6 | PASS |
| Traces | 56 | 56 | PASS |
| Symptoms | 48 | 48 | PASS |
| Symptom groups | 7 | 7 | PASS |
| Programs | 9 | 9 | PASS |
| Scenarios | 53 | 53 | PASS |
| Fault scenarios | 44 | 44 | PASS |
| Healthy scenarios | 9 | 9 | PASS |
| Configured durations | ['30s'] | ['30s'] | PASS |

## Outcome counts in results.csv

Compared independently with each source run<N>_scores.csv. Each run also passes row-by-row identity, truth, verdict and outcome checks unless listed below.

| system | run | answers | FN | FN_cautious | FP | FP_unseeable | TN | TN_abstain | TP | correct_unseeable | wrong_unseeable | matches source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| traceassist | 1 | 516 | 10 | 1 | 24 | 0 | 319 | 13 | 137 | 12 | 0 | PASS |
| traceassist | 2 | 516 | 8 | 4 | 24 | 0 | 317 | 15 | 136 | 11 | 1 | PASS |
| traceassist | 3 | 516 | 6 | 4 | 22 | 0 | 316 | 18 | 138 | 12 | 0 | PASS |
| codex | 1 | 516 | 8 | 6 | 113 | 1 | 209 | 34 | 134 | 10 | 1 | PASS |
| tmll | 1 | 516 | 15 | 51 | 62 | 1 | 117 | 177 | 82 | 11 | 0 | PASS |
| llm_only | 1 | 516 | 10 | 96 | 42 | 0 | 49 | 265 | 42 | 11 | 1 | PASS |
| rag | 1 | 516 | 10 | 97 | 40 | 0 | 59 | 257 | 41 | 10 | 2 | PASS |

## Mismatches

None. All requested counts and all seven system/run outcome distributions match the source.


## Additional checks

- PASS: Traces with intentional event omissions.
- PASS: Trace index IDs.
- PASS: Answer-key coverage.
- PASS: Scenario coverage of captures.
- PASS: Question IDs.
- PASS: Question coverage in pairs.
- PASS: Capture metadata agrees with index.
- PASS: Pair, question, symptom, scenario and answer-key consistency.
- PASS: Expected fields blank on non-present pairs.
- PASS: traceassist run 1 answers.
- PASS: traceassist run 1 answer coverage.
- PASS: traceassist run 1 score coverage.
- PASS: traceassist run 1 row-by-row score and answer consistency.
- PASS: traceassist run 2 answers.
- PASS: traceassist run 2 answer coverage.
- PASS: traceassist run 2 score coverage.
- PASS: traceassist run 2 row-by-row score and answer consistency.
- PASS: traceassist run 3 answers.
- PASS: traceassist run 3 answer coverage.
- PASS: traceassist run 3 score coverage.
- PASS: traceassist run 3 row-by-row score and answer consistency.
- PASS: codex run 1 answers.
- PASS: codex run 1 answer coverage.
- PASS: codex run 1 score coverage.
- PASS: codex run 1 row-by-row score and answer consistency.
- PASS: tmll run 1 answers.
- PASS: tmll run 1 answer coverage.
- PASS: tmll run 1 score coverage.
- PASS: tmll run 1 row-by-row score and answer consistency.
- PASS: llm_only run 1 answers.
- PASS: llm_only run 1 answer coverage.
- PASS: llm_only run 1 score coverage.
- PASS: llm_only run 1 row-by-row score and answer consistency.
- PASS: rag run 1 answers.
- PASS: rag run 1 answer coverage.
- PASS: rag run 1 score coverage.
- PASS: rag run 1 row-by-row score and answer consistency.
- PASS: Total result rows.
- PASS: traceassist run 1 exported outcome counts.
- PASS: traceassist run 2 exported outcome counts.
- PASS: traceassist run 3 exported outcome counts.
- PASS: codex run 1 exported outcome counts.
- PASS: tmll run 1 exported outcome counts.
- PASS: llm_only run 1 exported outcome counts.
- PASS: rag run 1 exported outcome counts.
- PASS: Workbook deterministic serialization.
- PASS: Workbook sheets.
- PASS: Workbook round-trip data and formatting.
- PASS: All traces report unavailable mem probes.
- PASS: Consumed source files unchanged during build.

## Interpretation notes

- 53 scenario rows represent nine programs; three extra recordings make 56 traces.
- All traces have configured duration 30s. Actual trace spans are not measured by this exporter.
- Six cannot_see pairs: three memory-pressure pairs, two busy-waiting pairs, one crash without signals. The three event-omission recordings do not map one-to-one to these six pairs.
- The source pair generator checks unavailable required events before don't-care labels. Q13 on cachesvc-48be is therefore cannot_see although the allocation_churn scenario lists memory_pressure as don't-care. This is a source-defined precedence rule, not a label changed by this exporter.
- Outcome counts retain abstentions and unseeable outcomes; they are not silently folded into TP/FP/TN/FN.
- Array fields preserve original list elements, including numeric tolerance text. Full answers are unchanged in JSONL.

## Source fingerprint

Read and SHA-256 checked 3692 source files. The sorted manifest uses `relative_path<TAB>sha256<LF>`; paths are relative to ../repo. Its SHA-256 is `fc720b169a23f8cf17ed92b8aa1e9751a776676b0c506a04fe9900d358785f9e`.

The source files are opened only for reading. No source generator, scorer or module is executed. Documentation inputs include the paper's bench, threats and introduction sections and capture.sh to substantiate collection details.

Core input fingerprints:

| Source | SHA-256 |
| --- | --- |
| bench/questions.json | ffaa8fd5dc6c04cadb1dbd3a4b48e7da8a22f988f9da68d12e1932bf3e664f51 |
| bench/pairs.json | 5268528049a3c31e6da44351ff3ddc9af690bcd4fce95425d75eb89ba30b4e08 |
| bench/answer_key.json | 39f8d7b69f81bc0959b3463d604adba8673f8518f801be3354ce083952b19b3f |
| bench/symptoms.json | b1786869e8c1b33b24313495ad868ab9fb8c7da559fd31289bc72cc94c5f82c8 |
| bench/scenarios.json | e41d82328d22807b812b0113da320d94e591cc59db38e1091d3099917a243e1f |
| bench/runs/index.csv | bf2a7b7bad9c308582311fbd9091a9064d15fc94b8e9b96a98477b77b50ac5b6 |

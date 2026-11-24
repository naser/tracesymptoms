# TraceSymptoms

TraceSymptoms is a benchmark for natural-language questions about Linux kernel traces, with
**negative controls**: every question is asked of traces where its symptom is present and of traces
where it is absent, so it measures false alarms as well as answers. It accompanies the ICPE 2027
industrial paper *Let Code Measure, Let the LLM Explain: Answering Kernel Trace Questions with
TraceAssist* (Patel, Sehgal, Panahandeh, Tetreault, Ezzati-Jivan).

| | |
|---|---|
| Programs | 9 C programs with a `--fault` switch (44 faults + 9 healthy runs = 53 scenarios) |
| Symptoms | 48, in 7 groups |
| Traces | 56 LTTng kernel traces, 30 s each (1.4–25.3 M events) |
| Questions | 56, each in a precise and an everyday wording (112) |
| Question–trace pairs | 258 (74 present, 178 absent, 6 the trace cannot show) |
| Answer keys | written by the programs themselves while they run |

## Where things are

| Repository | Contents |
|---|---|
| **this repository** | The benchmark as release tables (`dataset/`), every system's verdicts and answers, and the analyses reported in the paper (`analysis/`) |
| [sneh2001patel/traceassist-icpe2027](https://github.com/sneh2001patel/traceassist-icpe2027) | TraceAssist's code (frozen build), the bench programs and recording scripts, the baselines, the raw results and the scorer |
| this repository (to be added) | The 56 trace archives and the baselines' inputs |

## `dataset/`

- `items.csv` / `items.jsonl`: one row per question–trace pair, with both wordings, symptom, group,
  category, hub scope, program, trace, fault, truth, and for present pairs the expected answer
  (threads, cause, numbers with tolerance, acceptable fixes).
- `symptoms.csv`, `programs.csv`, `traces.csv`: the 48 symptoms, 53 scenarios and 56 traces.
- `results.csv` / `results.jsonl`: every verdict (and, in the `.jsonl`, the full answer) of TraceAssist
  (3 runs), Codex, LLM + TMLL, RAG and LLM only (1 run each): 3,612 answers.
- `TraceSymptoms.xlsx`: the same tables in one workbook.
- `DATASET_CARD.md`, `composition.md` / `.tex`, `CHECKS.md` (64 consistency checks against the source).
- `build_dataset.py`: rebuilds everything from a checkout of the code repository.

The benchmark can be regenerated on another machine and kernel with the programs and
`capture.sh` in the code repository; each new recording writes a fresh answer key. The 56 traces on
this repository (once added) are the reference set for the paper's results.

## `analysis/`

- `codex_false_alarms/`: classification of the Codex agent's 113 false-alarm answers and of
  TraceAssist's 24 (one annotator, after the runs).
- `content_audit/`: grading of 60 matched present answers per system against the answer keys.
  The sample (`sample.json`, fixed seed, hash in `sample_hash.txt`) and the rubric (`RUBRIC.md`) were
  fixed before grading. Two graders (a GPT-6 model and a Claude model) graded blind to the system
  (`grades_*.json`; `blind_mapping.json` maps A/B to systems); the authors resolved the 18
  disagreements (`adjudicated.json`). `final.py` gives
  the reported numbers (`final_results.json`).
- `soundness/`: cluster-bootstrap confidence intervals, strict scoring and sensitivity checks.

Scripts read the code repository from `../traceassist-icpe2027` by default, or from `$TRACEASSIST_REPO`.

## Licence

Code (scripts) under the MIT licence (`LICENSE`); data under CC BY 4.0 (`LICENSE-DATA`).
The traces are whole-machine recordings of one desktop and show its own processes and file paths.

# TraceSymptoms release tables

Rebuild with `python3 build_dataset.py` from this folder. The builder reads a checkout of traceassist-icpe2027 at `../repo` (or `$TRACEASSIST_REPO`)
and writes only beside itself. It requires Python 3.9+ and openpyxl. If openpyxl is
missing, it creates or uses `./.venv` and installs openpyxl 3.1.5 there. Cached wheels
in `.venv/wheels` are used offline when available. No API or model calls are made.
Ordering and workbook timestamps are fixed; repeated builds with unchanged sources
and the same dependency versions produce identical bytes. `CHECKS.md` records source
fingerprints, validation results and any mismatches; a failed check exits nonzero.

| File | Unit of observation |
| --- | --- |
| items.csv / items.jsonl | One question–trace pair (258) |
| symptoms.csv | One catalog symptom (48) |
| programs.csv | One program/fault scenario (53 rows, nine programs) |
| traces.csv | One recording (56) |
| results.csv / results.jsonl | One item, wording, system and run (3,612) |
| TraceSymptoms.xlsx | The same tables; README plus five data sheets |
| composition.md / composition.tex | Counts; LaTeX requires booktabs |
| DATASET_CARD.md | Collection, recommended use and limitations |
| CHECKS.md | Counts, joins, source consistency and result reconciliation |

## Fields and joins

`item_id` is derived as `<question_id>__<trace_id>` (for example,
`Q1__jobrunner-5497`). `question_id` identifies a question without a wording suffix.
In Results, `wording=a` means precise and `wording=b` means everyday. `run` is the
system repetition number, not a trace ID. Join Results to Items on `item_id`, Items
to Symptoms on `symptom_id=id`, and Items to Traces on `trace_id`. Join a trace to
Programs on `(program, fault)`. Rows are sorted by numeric question ID and trace ID;
results then use wording, the documented system/run order. Other tables use their IDs.

List-valued fields are compact JSON arrays stored as text in CSV, JSONL and Excel.
Empty lists are blank strings. This preserves list boundaries and the source text.
`expected_numbers` retains the source numbers, units and tolerances verbatim inside
that text array. `expected_where_any` and `expected_fixes` list acceptable alternatives;
`expected_where_all` lists jointly required locations. All `expected_*` fields are
blank for absent and cannot_see pairs. Empty expected lists on present pairs mean the
source supplied no entries. `role` is copied unchanged from pairs.json.

Symptoms maps `criterion` to `definition_present`, `asked` to `how_users_ask`,
`requires` to `events_required`, and `helps` to `events_helpful`. Programs maps
`description` to `workload`, and each fault's `summary`, `present` and `dont_care`
to the corresponding columns. Categories and hub values are source identifiers.
Single-hub concerns one thread/process; multi-hub combines evidence across several.

`duration` preserves capture.json's configured duration string (`30s`). It is not
the measured first-to-last-event span. `recorded_at` retains its source timezone.
Event columns contain event-group identifiers, not individual event counts.
`events_left_out` records intentional omissions only. Unavailable probes are distinct:
the source reports `mem` unavailable on all 56 traces; do not treat a blank
`events_left_out` as proof that every probe was available.

| group | source description |
| --- | --- |
| base | sched_*, timer/IRQ, x86 IRQ vectors, all syscalls, statedump (always recorded) |
| block | block_* (disk requests issued and completed) |
| mem | kmem_* and page-fault events (no probe for them on this machine's kernel) |
| net | net_*, netif_* (packets sent and received) |
| signal | signal_generate, signal_deliver |

## Results and scoring

Results uses each saved JSON's verdict and recomputes outcome using the rules in
`bench/score.py`. Both are compared row by row and by outcome counts with the stored
score CSV, and verdicts are checked against the full answer's verdict line. Run and
elapsed seconds stay numeric in JSONL and Excel. An unavailable elapsed time is blank,
not zero. `results.jsonl` adds `answer`, preserving the full source answer text.
CSV and Excel contain no answer text, tool transcripts or API response objects.

| Truth | present verdict | absent verdict | cannot_tell verdict |
| --- | --- | --- | --- |
| present | TP | FN | FN_cautious |
| absent | FP | TN | TN_abstain |
| cannot_see | FP_unseeable | wrong_unseeable | correct_unseeable |

For the main confusion matrix, combine FN + FN_cautious and TN + TN_abstain.
Unseeable outcomes are reported separately. A missing verdict is blank with outcome
`no_verdict`, excluded by the source scorer; none is silently converted to absent.
This release contains all answers in the requested runs, including errors if any;
status and completeness discrepancies are reported in CHECKS.md.

Ground-truth tables and saved answers are evaluation material, not system inputs.
The source repository's data/README.md describes obtaining the trace archives.
No redaction or paraphrasing has been applied to the source answer text.
Pair labelling checks event availability before scenario don't-care labels. In
particular, Q13 on cachesvc-48be is cannot_see because mem probes are unavailable,
although memory_pressure is don't-care for that allocation_churn scenario.
Licence and citation remain TBD; see DATASET_CARD.md.

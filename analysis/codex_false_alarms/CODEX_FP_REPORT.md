# Why does the Codex baseline say "yes" on symptom-absent traces? (run 1)

## Question tested

Hypothesis under test: *Codex usually measured something real but judged a normal-sized effect as the
problem (no sense of scale or threshold), rather than mis-measuring.*

Short answer: **partly supported.** Codex almost never mis-measured (6 of 113 FPs). But only about half of
its FPs (54/113, 48%) are scale or threshold errors in the narrow sense. Another 28% (32) come from reading
*designed* behaviour as a fault, such as an input-pacing sleep, a coordinator waiting for its workers, the
harness watchdog, or the dynamic loader. Those effects are often large, so the missing piece is a model of
what the program is meant to do, not a sense of scale. A further 19% (21) are real, abnormal effects of the
trace's own fault matched to a neighbouring symptom. More than half of those (13) are defensible yeses under
the everyday wording. The phrase "no sense of scale" is also too strong: in 40/113 FPs (21 of the 50 SCALE
cases), Codex's own answer says the effect is small, brief, rare or not sustained, and the verdict line still
says yes. The weak point is turning a finding into a verdict ("does X happen at all?" is answered yes), not
noticing the size of the finding.

## Method

- Data: `bench/results/{codex,traceassist}/run1_scores.csv` and the `run1/<id>.json` answers. The repo was not
  modified.
- Population: every row with `outcome == FP`. That is 113 for Codex and 24 for TraceAssist. Codex's single
  `FP_unseeable` row (Q2b, crunch-3329) is excluded, as the brief asked.
- For each FP I read the answer next to the symptom's written criterion (`symptoms.json`), the question text,
  and the trace's fault summary (`answer_key.json`). Where a design fact mattered, I checked the bench program's
  source. Examples: batch_server pins all threads to one CPU; pipeline's reader is paced at 2000 items/s;
  jobrunner dispatches a job every 10 ms. Every answer was unambiguous enough that I did not need the
  transcripts.
- Each FP got one primary category, plus two flags: `self_contradicting` (the answer body says the effect is
  small or not the symptom, but the verdict is yes) and `label_debatable` (a careful human could defend "yes"
  given the question as worded).
- Categories (the brief's set, with two added and one renamed):
  - **SCALE**: a real effect that is of normal size, rare or brief, called the symptom.
  - **THRESHOLD**: a precise-wording question states a threshold or qualifier. Codex's own numbers fail it, or
    pass it only through an extreme statistic (one max−min pair, a 20 ms window, a reframed denominator).
  - **INTERPRETATION**: normal design behaviour read as the fault (pacing sleep, coordinator wait, watchdog,
    loader, periodic stats call, the SIGKILL that `exit_group` sends to sibling threads).
  - **ADJACENT** (new): a real, abnormal effect of the trace's actual fault, mapped onto the asked symptom.
  - **LITERAL_TRUE** (new): by design, the everyday wording is literally true of the trace. "Absent" rests on a
    criterion condition that the question does not state.
  - **WRONG_ENTITY**: attributes another process's activity, or another thread role's, to the asked
    program or group.
  - **MISMEASURED**: a computation or identification error. MISMEASURED and WRONG_ENTITY correspond to the
    brief's "MISMEASURED" and "WRONG-ENTITY".
- Scripts: `analysis/labels_codex.py` and `labels_traceassist.py` hold the labels, the justifications and
  verbatim quotes. `build.py` checks that every quote is a substring of its answer and within the length limits,
  then writes `codex_fp_classified.csv`, `traceassist_fp_classified.csv` and `counts.md`.
- **One annotator, post hoc.** I knew the hypothesis while labelling. No second coder and no agreement
  statistic. Treat the boundaries as soft, especially SCALE/THRESHOLD/INTERPRETATION and ADJACENT/LITERAL_TRUE.

## Counts

| Category | Codex n (%) | self-contradicting | label-debatable | TraceAssist n (%) |
|---|---:|---:|---:|---:|
| SCALE | 50 (44%) | 21 | 9 | 6 (25%) |
| THRESHOLD | 4 (4%) | 4 | 0 | 0 |
| INTERPRETATION | 32 (28%) | 9 | 0 | 2 (8%) |
| ADJACENT | 17 (15%) | 5 | 9 | 12 (50%) |
| LITERAL_TRUE | 4 (4%) | 0 | 4 | 4 (17%) |
| WRONG_ENTITY | 3 (3%) | 1 | 0 | 0 |
| MISMEASURED | 3 (3%) | 0 | 0 | 0 |
| **All** | **113** | **40** | **22** | **24** (14 self-contradicting, 14 label-debatable) |

Grouped against the hypothesis (Codex):

- Measured right, judged the size wrong (SCALE + THRESHOLD): **54 (48%)**. In 25 of these, the answer itself
  states the effect is small.
- Measured right, judged the *intent* wrong (INTERPRETATION): **32 (28%)**.
- Real fault effect, neighbouring symptom (ADJACENT + LITERAL_TRUE): **21 (19%)**. 13 are label-debatable.
- Mis-measured or wrong entity: **6 (5%)**.
- 42 of the 113 FPs are on healthy (`fault none`) traces. All of those are SCALE (22), INTERPRETATION (15),
  THRESHOLD (2), WRONG_ENTITY (2) or LITERAL_TRUE (1).

### Category × wording (a = precise, b = everyday)

| | Codex a | Codex b | TA a | TA b |
|---|---:|---:|---:|---:|
| SCALE | 14 | 36 | 3 | 3 |
| THRESHOLD | 4 | 0 | 0 | 0 |
| INTERPRETATION | 13 | 19 | 1 | 1 |
| ADJACENT | 3 | 14 | 2 | 10 |
| LITERAL_TRUE | 0 | 4 | 0 | 4 |
| WRONG_ENTITY | 0 | 3 | 0 | 0 |
| MISMEASURED | 3 | 0 | 0 | 0 |
| **FPs / absent pairs** | **37/178 (21%)** | **76/178 (43%)** | **6/178 (3%)** | **18/178 (10%)** |

Stating the threshold halves Codex's FP rate but leaves it at 21%. With precise wording, Codex mostly
passes the threshold through a convenient statistic or a reframed denominator, or ignores a qualifier such as
"throughout the run". It rarely reports a number below the threshold outright.

### Category × symptom group (Codex)

| | cpu | lifecycle | pipelines | syscalls_io | timing | unexpected | waiting |
|---|---:|---:|---:|---:|---:|---:|---:|
| SCALE | 15 | 3 | 0 | 11 | 5 | 10 | 6 |
| THRESHOLD | 0 | 2 | 0 | 0 | 1 | 0 | 1 |
| INTERPRETATION | 2 | 3 | 5 | 1 | 0 | 10 | 11 |
| ADJACENT | 2 | 0 | 0 | 6 | 5 | 0 | 4 |
| LITERAL_TRUE | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| WRONG_ENTITY | 1 | 0 | 0 | 1 | 0 | 1 | 0 |
| MISMEASURED | 0 | 0 | 0 | 0 | 3 | 0 | 0 |
| total | 20 | 8 | 5 | 19 | 14 | 21 | 26 |

TraceAssist, by group: waiting 12, cpu 5, lifecycle 2, timing 2, unexpected 2, syscalls_io 1.
Its 4 LITERAL_TRUE and 5 of its 12 ADJACENT FPs are in the waiting group.

### Overlap on the same pair and wording

- Of the 113 Codex FPs, TraceAssist got **93 TN** and 4 TN_abstain on the same question, wording and trace.
  The other 16 are FPs for both systems.
- By Codex category, TraceAssist was right (TN or TN_abstain) on: SCALE 46/50, THRESHOLD 4/4,
  INTERPRETATION 31/32, WRONG_ENTITY 3/3, MISMEASURED 3/3, but only ADJACENT 10/17 and LITERAL_TRUE 0/4.
- So TraceAssist's advantage comes almost entirely from SCALE and INTERPRETATION cases. The FPs the two
  systems share are mostly the label-debatable ADJACENT and LITERAL_TRUE pairs.

### Effort (Codex, medians)

| outcome | n | n_commands | elapsed_s | output tokens |
|---|---:|---:|---:|---:|
| TP | 134 | 16 | 218 | 11,656 |
| FP | 113 | 16 | 221 | 11,498 |
| TN | 209 | 16 | 210 | 11,287 |
| FP: SCALE | 50 | 15 | 172 | 9,413 |
| FP: INTERPRETATION | 32 | 17 | 259 | 12,399 |
| FP: ADJACENT | 17 | 18 | 256 | 13,293 |

Effort does not distinguish TPs from FPs: Mann–Whitney p = 0.98 for n_commands and p = 0.75 for elapsed_s. SCALE
FPs are somewhat quicker than the rest. That fits finding one qualifying event and stopping, but it is weak
evidence.

## Representative examples (Codex)

1. **THRESHOLD, self-contradicting.** `Q10a__jobrunner-b074` (healthy trace, thread churn, precise wording
   "tens per second or more"). Codex found the 5 normal start-up threads and rated them over the 20 ms burst
   to get "about 250 creations per second". It then wrote: "This is a brief create-and-exit burst, not sustained
   thread churn." Verdict: yes.
2. **SCALE, self-contradicting.** `Q1b__jobrunner-0dd3` (slow start-up). Codex measured 107 ms, then wrote
   "it is about a tenth of a second rather than seconds". Verdict: yes. Other cases in this pattern: 50 µs hrtimer
   slack reported as the timer firing late (`Q12b__ticker-d731`, criterion 1 ms), and 10 opens per second as
   file churn (`Q4b__filestore-5705`, criterion hundreds per second).
3. **INTERPRETATION.** `Q17a__pipeline-9a66` (healthy trace, bottleneck, precise "25% faster"). The reader is
   designed to produce 2000 items/s, so it sleeps 0.5 ms between items. Codex took those sleeps as removable
   delay, computed the counterfactual run time, and concluded "The evidence strongly supports clearing that
   threshold." The same misreading of the reader drives 15 FPs on pipeline (Q8/Q17/Q25): "the reader is idle", "the reader is
   the bottleneck", "the reader is the slow stage". In `Q25a__pipeline-9a66`, Codex itself notes that it "cannot
   establish whether that pacing is a performance problem or a configured rate".
4. **INTERPRETATION.** `Q5a__jobrunner-b074` (healthy trace, crash). When the main thread calls `exit_group`,
   the kernel delivers SIGKILL to the watchdog thread. Codex read this as "The `jobrunner` process (PID/TGID
   652157) was killed by **SIGKILL (signal 9)**."
5. **LITERAL_TRUE.** `Q32b__batch_server-8824` (healthy trace). batch_server pins all its threads to one CPU
   by design, so the workers do run one after another. Codex measured this correctly and gave the right cause:
   "The trace supports single-CPU execution as the reason they cannot run in parallel". The "absent" truth
   depends on the convoy criterion's "because of a shared lock", which the everyday question does not mention.
   TraceAssist also says yes on all four Q32b pairs.
6. **MISMEASURED.** `Q14a__jobrunner-7489` (crash fault). Codex took the 5-second helper fork as the "last
   job" ("about **4.931 seconds after its last job-helper finished**"). In fact the dispatcher queues a job
   every 10 ms until exit. TraceAssist measured a 0.12 ms shutdown here.

TraceAssist's FPs have a different profile. All 6 of its SCALE FPs are self-contradicting: the findings
already label the effect, e.g. 0.14 thread creations/s "labeled a low rate" or a 0.24 ms straggler "labels its
hold-up negligible", and the writer still says yes. Most of its other FPs (16 of 18) are ADJACENT or LITERAL_TRUE
cases on traces with a real, different fault, and 14 of 24 are label-debatable.

## What the data say about the hypothesis

- **"Rather than mis-measuring": supported.** Only 6/113 FPs (5%) come from a measurement or attribution
  error. Codex's numbers, as far as the answers show, are plausible and often detailed. I did not re-measure
  them independently.
- **"Judged a normal-sized effect as the problem": supported for about half.** 54/113 (48%).
- **"No sense of scale": not the best description.** In 25 of these 54 cases, Codex's prose states the effect
  is small or not sustained. The verdict follows an existence reading ("does X occur?") rather than the
  criterion. The prompt's mandatory first line, "Verdict: yes / no / cannot tell", may encourage this, but
  TraceAssist's writer gets the same prompt and makes the same mistake in 6 of its 24 FPs.
- **A second, distinct cause: no model of design intent** (28%). Pacing sleeps, coordinator waits for
  workers, periodic stats calls, the watchdog and the loader are not small effects. Codex lacks a baseline for
  what the program is supposed to do. TraceAssist avoids these almost completely (31/32 TN on the same pairs).
  Its findings separate waits for new work and timed sleeps from waits with work pending, though it still makes
  the coordinator-wait error once (`Q26a__batch_server-8824`, as Codex does).
- **About a fifth of Codex's FPs, and well over half of TraceAssist's, are arguably benchmark-label issues.**
  These are everyday questions that are literally true of a faulty, or by-design odd, trace: Q28b loopback "remote
  server", Q32b single-CPU workers, Q38b step vs gradual slowdown, Q45b/Q46b real CPU hogs, Q51b/Q54b real
  disk_wait and convoy effects. This affects both systems and narrows the measured gap a little. Even if all 22
  label-debatable Codex FPs were re-scored as correct, Codex would still have 91 FPs against TraceAssist's 10.

## Caveats

- One annotator, labelling post hoc with the hypothesis in mind. No inter-rater agreement. Category boundaries
  (SCALE vs THRESHOLD vs INTERPRETATION; ADJACENT vs LITERAL_TRUE) are judgment calls. The CSV keeps a
  justification and a verbatim quote for every row so that others can re-label.
- I judged answer text only. I did not re-run any measurement on the traces, so "measured something real"
  means "plausible and internally consistent", not "verified".
- This covers run 1 only. The FPs cluster on a few traces (e.g. ticker-d731, pipeline-9a66, batch_server-8824,
  filestore-5705), so the 113 are not independent: one misreading of a program's design produces several FPs.
- The 4 THRESHOLD cases are a narrow reading: only cases where Codex's own numbers, or an ignored qualifier,
  contradict a stated threshold. Many precise-wording SCALE cases (14) also involve a threshold the answer never
  engages with.
- The `label_debatable` flag is my opinion, not a re-scoring. The ground truth follows the written criteria in
  `SYMPTOMS.md`, which the systems were not shown.

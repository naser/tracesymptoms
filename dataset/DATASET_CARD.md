# TraceSymptoms dataset card

**Motivation.** TraceSymptoms tests natural-language questions about Linux kernel traces.
Healthy runs and other faults serve as negative controls, so evaluation measures false
alarms as well as detection.

**Composition.** Nine C workloads have 44 fault switches and nine healthy configurations:
53 scenarios, recorded as 56 LTTng kernel traces with a configured duration of 30 s.
The catalog has 48 symptoms in seven groups. There are 56 questions, each in precise
(a) and everyday (b) wording: 112 wordings and 258 question–trace pairs (74 present,
178 absent, six cannot_see). Each system/run has 516 answers. The release includes
TraceAssist runs 1–3 and one run each for Codex, TMLL, LLM only and RAG: 3,612 answers.
Tables and saved answers are included here; trace binaries remain in the source release.

**Collection.** Each program runs one workload with one selected fault, or none.
It writes its own answer key through anonymous pipes, including symptom labels,
thread IDs, fault intervals and measurements. Thresholds were chosen by measuring each
symptom on every trace of its program. Thread, process and file names do not name the
fault; trace IDs use a program prefix and random suffix. Three scenarios were recorded
again without an event group: crash without signals, disk wait without block events,
and network wait without network events. The duration field records the configured
duration, not an independently measured trace span.

**Labelling.** Truth belongs to a question–trace pair. Don't-care symptoms are not
graded as present or absent; unavailable required events take precedence and produce
cannot_see, as specified in the pair generator. Labels account for the distinctions the
trace can show. The six cannot_see pairs concern missing memory probes (three), a crash
without signal events (one), and spin-waiting versus computation (two). The current pair
labels are authoritative; omitting an event group does not make every question about
that trace unanswerable. Expected locations, causes, numbers with tolerances and fixes
are copied from the answer key only for present pairs. The harness watchdog alone is
not evidence of a symptom.

**Use and scoring.** Give a tested system only the question, the standard verdict
instruction and the trace. Keep fault metadata, truth, expected answers and saved
system answers out of its inputs. From the source repository root, run
`python3 bench/score.py --system X` (add `--run 2` or `--run 3` for TraceAssist).
The scorer uses the saved verdict field. Abstention is FN_cautious on present pairs
and TN_abstain on absent pairs. On cannot_see pairs, it is correct_unseeable; a positive
is FP_unseeable and a negative is wrong_unseeable. Report those separately from the
504 present/absent answers per run. Verdict scores do not grade locations, causes,
numbers or fixes. Compare wordings and report false alarms alongside detection.

**Limits.** All recordings use one machine and kernel, short runs, small programs and
one fault at a time. The authors wrote the questions after the question types of
industrial engineers; these are not a sampled corpus of industrial queries. Thresholds
and TraceAssist were developed using this bench. Whole-machine recordings also show
the recording desktop's own processes, names, paths and user name; saved answers may
repeat them. Missing probes and kernel-only evidence limit what can be established.

**Licence:** TBD. **Citation:** TBD.

**Sources:** `bench/{questions,pairs,answer_key,symptoms,scenarios}.json`,
`bench/runs/{index.csv,*/capture.json}`, `bench/results/`, repository and bench READMEs,
`QUESTIONS.md`, `SYMPTOMS.md`, `bench/{capture.sh,make_pairs.py}`, and `paper/sections/{bench,threats,introduction}.tex`.

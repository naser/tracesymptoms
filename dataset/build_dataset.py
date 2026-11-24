#!/usr/bin/env python3
"""Build TraceSymptoms from the read-only ../repo, writing only beside this script.

Run: python3 build_dataset.py
Dependencies: Python >= 3.9, openpyxl 3.1.5 (installed in .venv if missing).
All record ordering, JSON serialization, workbook properties and ZIP timestamps
are fixed. No source program, scorer, or generator is executed or imported.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import venv
import zipfile
from collections import Counter
from datetime import datetime

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("TRACEASSIST_REPO", HERE.parent / "repo"))
BENCH = REPO / "bench"
RUNS = [("traceassist", 1), ("traceassist", 2), ("traceassist", 3),
        ("codex", 1), ("tmll", 1), ("llm_only", 1), ("rag", 1)]
TRUTHS = ["present", "absent", "cannot_see"]
ITEM_FIELDS = "item_id question_id wording_precise wording_everyday symptom_id symptom_name symptom_group category hub_scope program trace_id trace_fault events_left_out truth role expected_where_any expected_where_all expected_cause expected_numbers expected_fixes".split()
SYMPTOM_FIELDS = "id group name definition_present how_users_ask events_required events_helpful category hub".split()
PROGRAM_FIELDS = "program workload fault fault_description present_symptoms dont_care_symptoms".split()
TRACE_FIELDS = "trace_id program fault duration events_recorded events_left_out recorded_at".split()
RESULT_FIELDS = "item_id wording system run verdict outcome elapsed_s".split()
OUTPUTS = ["items.csv", "items.jsonl", "symptoms.csv", "programs.csv", "traces.csv",
           "results.csv", "results.jsonl", "TraceSymptoms.xlsx", "composition.md",
           "composition.tex", "DATASET_CARD.md", "CHECKS.md", "README.md"]
SOURCE_HASHES = {}
CHECKS = []


def dependencies():
    try:
        import openpyxl  # noqa: F401
        return
    except ImportError:
        pass
    local = HERE / ".venv"
    python = local / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(local)
    probe = subprocess.run([str(python), "-c", "import openpyxl"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if probe.returncode:
        command = [str(python), "-m", "pip", "install", "--disable-pip-version-check",
                   "--no-cache-dir"]
        wheels = local / "wheels"
        if list(wheels.glob("openpyxl-*.whl")):
            command += ["--no-index", "--find-links", str(wheels)]
        subprocess.run(command + ["openpyxl==3.1.5"], check=True, cwd=HERE)
    os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])


def read(path):
    data = path.read_bytes()
    SOURCE_HASHES[path.relative_to(REPO).as_posix()] = hashlib.sha256(data).hexdigest()
    return data.decode("utf-8")


def read_json(path):
    return json.loads(read(path))


def read_csv(path):
    return list(csv.DictReader(io.StringIO(read(path), newline="")))


def check(name, actual, expected):
    CHECKS.append((name, actual == expected, actual, expected))


def unique(rows, key, name):
    result = {}
    for row in rows:
        k = key(row)
        if k in result:
            raise ValueError(f"Duplicate {name}: {k!r}")
        result[k] = row
    return result


def list_text(value):
    """Lossless JSON array in a text cell; an empty list is a blank cell."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) if value else ""


def text_file(name, value):
    with (HERE / name).open("w", encoding="utf-8", newline="\n") as f:
        f.write(value)


def csv_file(name, fields, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)


def jsonl_file(name, rows):
    text_file(name, "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":"),
                                      allow_nan=False) + "\n" for row in rows))


def qsort(qid):
    return int(qid[1:])


# Same classification as bench/score.py:outcome, kept local to avoid running source code.
def outcome(truth, verdict):
    if not verdict:
        return "no_verdict"
    return {
        "present": {"present": "TP", "absent": "FN", "cannot_tell": "FN_cautious"},
        "absent": {"present": "FP", "absent": "TN", "cannot_tell": "TN_abstain"},
        "cannot_see": {"present": "FP_unseeable", "absent": "wrong_unseeable",
                       "cannot_tell": "correct_unseeable"},
    }[truth][verdict]


# Pattern from bench/verdict.py; used to check saved verdicts against full answers.
VERDICT = re.compile(r"^[\s>#*_`-]*verdict\s*[:\-]\s*[*_`]*\s*(yes|no|cannot tell|can't tell|"
                     r"can not tell|unknown|unclear)\b", re.IGNORECASE | re.MULTILINE)


def parse_verdict(answer):
    match = VERDICT.search(answer)
    return {"yes": "present", "no": "absent"}.get(match[1].lower(), "cannot_tell") if match else ""


def table(headers, rows):
    def escape(value):
        return str(value).replace("|", "\\|").replace("\n", "<br>")
    lines = ["| " + " | ".join(map(escape, headers)) + " |",
             "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines += ["| " + " | ".join(map(escape, row)) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def composition(items, questions):
    tables = []
    categories = sorted({q["category"] for q in questions})
    hubs = sorted({q["hub"] for q in questions}, reverse=True)
    counts = Counter((q["category"], q["hub"]) for q in questions)
    rows = [[cat, *[counts[cat, h] for h in hubs], sum(counts[cat, h] for h in hubs)]
            for cat in categories]
    rows.append(["Total", *[sum(counts[c, h] for c in categories) for h in hubs], len(questions)])
    tables.append(("Category by hub (unique questions)", ["category", *hubs, "Total"], rows))
    for field, title in [("symptom_group", "Symptom group by truth (pairs)"),
                         ("program", "Program by truth (pairs)")]:
        values = sorted({r[field] for r in items})
        counts = Counter((r[field], r["truth"]) for r in items)
        rows = [[v, *[counts[v, t] for t in TRUTHS], sum(counts[v, t] for t in TRUTHS)] for v in values]
        rows.append(["Total", *[sum(counts[v, t] for v in values) for t in TRUTHS], len(items)])
        tables.append((title, [field, *TRUTHS, "Total"], rows))
    counts = Counter(r["truth"] for r in items)
    rows = [[w, *[counts[t] for t in TRUTHS], len(items)] for w in ["a (precise)", "b (everyday)"]]
    rows.append(["Total", *[2 * counts[t] for t in TRUTHS], 2 * len(items)])
    tables.append(("Wording by truth (answers per system/run)", ["wording", *TRUTHS, "Total"], rows))
    md = ["# TraceSymptoms composition\n", "Counts are computed from unique questions and exported items. "
          "The wording table describes one system/run (516 answers), not the seven runs combined.\n"]
    tex = ["% Generated by build_dataset.py. Requires \\usepackage{booktabs}.",
           "% Wording counts refer to one system/run; question counts do not double-count wordings."]
    escapes = {"_": r"\_", "&": r"\&", "%": r"\%", "#": r"\#", "$": r"\$",
               "{": r"\{", "}": r"\}", "\\": r"\textbackslash{}"}
    latex = lambda value: "".join(escapes.get(c, c) for c in str(value))
    for index, (title, headers, rows) in enumerate(tables, 1):
        md += ["## " + title + "\n", table(headers, rows)]
        tex += [r"\begin{table}[htbp]", r"\centering", r"\caption{" + latex(title) + "}",
                r"\label{tab:benchname-composition-" + str(index) + "}",
                r"\begin{tabular}{l" + "r" * (len(headers) - 1) + "}", r"\toprule",
                " & ".join(map(latex, headers)) + " " + chr(92) * 2, r"\midrule"]
        for row in rows:
            if row[0] == "Total":
                tex.append(r"\midrule")
            tex.append(" & ".join(map(latex, row)) + " " + chr(92) * 2)
        tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    text_file("composition.md", "\n".join(md))
    text_file("composition.tex", "\n".join(tex))


def workbook_bytes(sheets, notes):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.table import Table, TableStyleInfo

    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = "TraceSymptoms"
    wb.properties.title = "TraceSymptoms research benchmark"
    wb.properties.created = wb.properties.modified = datetime(2000, 1, 1)
    sheets = [("README", ["topic", "description"], notes)] + sheets
    widths = {"item_id": 39, "question_id": 13, "wording_precise": 65, "wording_everyday": 55,
              "symptom_id": 30, "symptom_name": 37, "symptom_group": 19, "category": 20,
              "hub_scope": 15, "program": 19, "trace_id": 25, "trace_fault": 27,
              "expected_cause": 65, "expected_numbers": 60, "expected_fixes": 60,
              "definition_present": 70, "how_users_ask": 55, "workload": 65,
              "fault_description": 80, "present_symptoms": 48, "dont_care_symptoms": 48,
              "recorded_at": 30, "topic": 25, "description": 105, "elapsed_s": 14,
              "events_recorded": 36, "outcome": 25}
    for name, fields, rows in sheets:
        ws = wb.create_sheet(name)
        ws.append(fields)
        for row in rows:
            ws.append([row[field] if row[field] != "" else None for field in fields])
        ws.freeze_panes = "A2" if name == "README" else "B2"
        ws.sheet_view.showGridLines = False
        for col, field in enumerate(fields, 1):
            width = widths.get(field, min(45, max(18, len(field) + 3,
                          max((len(str(row[field])) for row in rows), default=0) + 1)))
            ws.column_dimensions[get_column_letter(col)].width = width
        for cells in ws.iter_rows():
            lines = 1
            for cell in cells:
                cell.font = Font(name="Arial", size=10)
                cell.alignment = Alignment(vertical="top", wrap_text=True,
                                           horizontal="right" if isinstance(cell.value, (int, float)) else "left")
                if isinstance(cell.value, str):
                    if len(cell.value) > 32767:
                        raise ValueError(f"Excel cell would truncate: {name}!{cell.coordinate}")
                    cell.data_type = "s"  # Preserve source text, including any leading '='.
                    width = ws.column_dimensions[cell.column_letter].width
                    lines = max(lines, sum(max(1, len(textwrap.wrap(part, width=max(8, int(width * .9)))))
                                           for part in cell.value.split("\n")))
            ws.row_dimensions[cells[0].row].height = max(24, lines * 14 + 8)
        for cell in ws[1]:
            cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="243746")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 34
        if name != "README":
            tab = Table(displayName=name + "Data", ref=ws.dimensions)
            tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
            ws.add_table(tab)
        if "elapsed_s" in fields:
            for cells in ws.iter_rows(min_row=2, min_col=fields.index("elapsed_s") + 1,
                                      max_col=fields.index("elapsed_s") + 1):
                cells[0].number_format = "0.00"
        ws.print_title_rows = "1:1"
    raw = io.BytesIO()
    wb.save(raw)
    # openpyxl sets modified at save time; normalize it and ZIP member timestamps.
    result = io.BytesIO()
    with zipfile.ZipFile(raw) as src, zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as dst:
        for name in sorted(src.namelist()):
            data = src.read(name)
            if name == "docProps/core.xml":
                data = re.sub(rb"(<dcterms:modified\b[^>]*>).*?(</dcterms:modified>)",
                              rb"\g<1>2000-01-01T00:00:00Z\2", data)
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o600 << 16
            dst.writestr(info, data, compresslevel=9)
    return result.getvalue()


def documents(event_groups):
    text_file("DATASET_CARD.md", """# TraceSymptoms dataset card

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
""")
    groups = table(["group", "source description"], sorted(event_groups.items()))
    text_file("README.md", """# TraceSymptoms release tables

Rebuild with `python3 build_dataset.py` from this folder. The builder reads `../repo`
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

""" + groups + """
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
""")


def main():
    dependencies()
    SOURCE_HASHES.clear()
    CHECKS.clear()
    # Read documentation used for prose and local reference implementations for provenance.
    for name in ["README.md", "QUESTIONS.md", "SYMPTOMS.md", "bench/README.md",
                 "bench/score.py", "bench/verdict.py", "bench/capture.sh",
                 "paper/sections/bench.tex", "paper/sections/threats.tex",
                 "paper/sections/introduction.tex"]:
        read(REPO / name)
    # Read the literal list of kernel-only ambiguities without executing the generator.
    generator = ast.parse(read(BENCH / "make_pairs.py"))
    unseeable = next(ast.literal_eval(n.value) for n in generator.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "UNSEEABLE" for t in n.targets))
    qs = read_json(BENCH / "questions.json")["questions"]
    pairs = read_json(BENCH / "pairs.json")["pairs"]
    keys = read_json(BENCH / "answer_key.json")["pairs"]
    catalog = read_json(BENCH / "symptoms.json")
    scenarios = read_json(BENCH / "scenarios.json")
    index = read_csv(BENCH / "runs/index.csv")
    symptoms = unique(catalog["symptoms"], lambda x: x["id"], "symptom")
    questions = unique(qs, lambda x: x["id"], "wording")
    pair_map = unique(pairs, lambda x: (x["question"], x["run_id"]), "pair")
    key_map = unique(keys, lambda x: (x["question"], x["run_id"]), "answer key")
    captures = [read_json(f) for f in sorted((BENCH / "runs").glob("*/capture.json"))]
    trace_map = unique(captures, lambda x: x["run_id"], "trace")
    index_map = unique(index, lambda x: x["run_id"], "trace index")
    fault_map = unique([dict(f, program=p["program"]) for p in scenarios for f in p["faults"]],
                       lambda x: (x["program"], x["name"]), "scenario")
    check("Questions", len({q["question"] for q in qs}), 56)
    check("Wordings", len(qs), 112)
    check("Pairs", len(pairs), 258)
    for t, n in zip(TRUTHS, [74, 178, 6]):
        check("Pairs: " + t, sum(p["truth"] == t for p in pairs), n)
    check("Traces", len(captures), 56)
    check("Symptoms", len(symptoms), 48)
    check("Symptom groups", len({s["group"] for s in symptoms.values()}), 7)
    check("Programs", len({s["program"] for s in scenarios}), 9)
    check("Scenarios", len(fault_map), 53)
    check("Fault scenarios", sum(f[1] != "none" for f in fault_map), 44)
    check("Healthy scenarios", sum(f[1] == "none" for f in fault_map), 9)
    check("Configured durations", sorted({c["duration"] for c in captures}), ["30s"])
    check("Traces with intentional event omissions", sum(bool(c["events_left_out"]) for c in captures), 3)
    check("Trace index IDs", sorted(index_map), sorted(trace_map))
    check("Answer-key coverage", sorted(key_map), sorted(pair_map))
    check("Scenario coverage of captures", sorted({(c["program"], c["fault"]) for c in captures}), sorted(fault_map))
    check("Question IDs", sorted({q["question"] for q in qs}, key=qsort), [f"Q{i}" for i in range(1, 57)])
    check("Question coverage in pairs", sorted({p["question"] for p in pairs}), sorted({q["question"] for q in qs}))
    trace_errors = []
    for c in captures:
        ix = index_map.get(c["run_id"], {})
        for field in ["program", "fault", "duration", "recorded_at", "events_left_out", "events_unavailable"]:
            value = c[field]
            if isinstance(value, list):
                value = ",".join(value)
            if value != ix.get(field):
                trace_errors.append(f"{c['run_id']} {field}: capture={value!r}, index={ix.get(field)!r}")
    check("Capture metadata agrees with index", trace_errors, [])
    items, join_errors = [], []
    for p in sorted(pairs, key=lambda p: (qsort(p["question"]), p["run_id"])):
        qid, tid = p["question"], p["run_id"]
        a, b = questions[qid + "a"], questions[qid + "b"]
        s, c, key = symptoms[p["symptom"]], trace_map[tid], key_map[qid, tid]
        for field in ["symptom", "program", "category", "hub"]:
            if not (p[field] == a[field] == b[field] == key[field]):
                join_errors.append(f"{qid} {tid}: inconsistent {field}")
        if (a["wording"], b["wording"]) != ("precise", "everyday"):
            join_errors.append(f"{qid}: inconsistent wording labels")
        if not (a["symptom_name"] == b["symptom_name"] == s["name"] and
                a["group"] == b["group"] == s["group"] and p["category"] == s["category"] and p["hub"] == s["hub"]):
            join_errors.append(f"{qid}: inconsistent symptom catalog")
        if (p["program"], p["fault"]) != (c["program"], c["fault"]):
            join_errors.append(f"{qid} {tid}: inconsistent capture scenario")
        if p["events_left_out"] != ",".join(c["events_left_out"]):
            join_errors.append(f"{qid} {tid}: inconsistent omitted events")
        if key["truth"] != p["truth"] or key["fault"] != p["fault"] or key["wordings"] != {"a": a["text"], "b": b["text"]}:
            join_errors.append(f"{qid} {tid}: inconsistent answer key")
        scenario = fault_map[p["program"], p["fault"]]
        missing = set(c["events_left_out"] + c["events_unavailable"])
        if set(s["requires"]) & missing or (p["symptom"], p["program"], p["fault"]) in unseeable:
            scenario_truth = "cannot_see"
        elif p["symptom"] in scenario["present"]:
            scenario_truth = "present"
        elif p["symptom"] in scenario["dont_care"]:
            scenario_truth = "dont_care"
        else:
            scenario_truth = "absent"
        if p["truth"] != scenario_truth:
            join_errors.append(f"{qid} {tid}: pair truth {p['truth']} differs from generator rule {scenario_truth}")
        e = key["expected"] if p["truth"] == "present" else {}
        if p["truth"] == "present" and set(e) != {"where_any", "where_all", "cause", "numbers", "fix_any"}:
            join_errors.append(f"{qid} {tid}: unexpected or missing expected-answer fields")
        row = dict(zip(ITEM_FIELDS, [qid + "__" + tid, qid, a["text"], b["text"], s["id"], s["name"],
            s["group"], p["category"], p["hub"], p["program"], tid, p["fault"],
            list_text(c["events_left_out"]), p["truth"], p["role"],
            list_text(e.get("where_any", [])), list_text(e.get("where_all", [])), e.get("cause", ""),
            list_text(e.get("numbers", [])), list_text(e.get("fix_any", []))]))
        items.append(row)
    check("Pair, question, symptom, scenario and answer-key consistency", join_errors, [])
    check("Expected fields blank on non-present pairs", [r["item_id"] for r in items if r["truth"] != "present"
          and any(r[f] for f in ITEM_FIELDS if f.startswith("expected_"))], [])
    symptom_rows = [dict(zip(SYMPTOM_FIELDS, [s["id"], s["group"], s["name"], s["criterion"],
        list_text(s["asked"]), list_text(s["requires"]), list_text(s["helps"]), s["category"], s["hub"]]))
        for s in sorted(symptoms.values(), key=lambda s: s["id"])]
    program_rows = [dict(zip(PROGRAM_FIELDS, [p["program"], p["description"], f["name"], f["summary"],
        list_text(f["present"]), list_text(f["dont_care"])]))
        for p in sorted(scenarios, key=lambda p: p["program"]) for f in sorted(p["faults"], key=lambda f: f["name"])]
    trace_rows = [dict(zip(TRACE_FIELDS, [c["run_id"], c["program"], c["fault"], c["duration"],
        list_text(c["events_recorded"]), list_text(c["events_left_out"]), c["recorded_at"]]))
        for c in sorted(captures, key=lambda c: c["run_id"])]
    results, comparisons = [], []
    expected_ids = {p["question"] + w + "__" + p["run_id"] for p in pairs for w in "ab"}
    for system, run in RUNS:
        folder = BENCH / "results" / system
        answers = [read_json(f) for f in sorted((folder / f"run{run}").glob("*.json"))]
        scores = read_csv(folder / f"run{run}_scores.csv")
        saved = unique(answers, lambda r: r["id"], f"{system}/{run} answer")
        scored = unique(scores, lambda r: r["id"], f"{system}/{run} score")
        label = f"{system} run {run}"
        check(label + " answers", len(answers), 516)
        check(label + " answer coverage", sorted(saved), sorted(expected_ids))
        check(label + " score coverage", sorted(scored), sorted(expected_ids))
        errors, result_subset = [], []
        for answer_id, a in sorted(saved.items()):
            q, w, tid = a["question_id"][:-1], a["question_id"][-1], a["run_id"]
            p = pair_map[q, tid]
            v = (a.get("verdict") or {}).get("verdict") or ""
            if a["system"] != system or a["run"] != run or a["status"] != "ok" or answer_id != q + w + "__" + tid:
                errors.append(answer_id + ": inconsistent metadata or status")
            if v != parse_verdict(a["answer"]):
                errors.append(answer_id + ": saved verdict differs from answer text")
            elapsed = a.get("elapsed_s")
            if elapsed is not None and (not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0):
                errors.append(answer_id + ": invalid elapsed_s")
            row = dict(zip(RESULT_FIELDS, [q + "__" + tid, w, system, run, v, outcome(p["truth"], v),
                                           elapsed if elapsed is not None else ""]))
            row["answer"] = a["answer"]
            results.append(row)
            result_subset.append(row)
            expected_score = {"question": q, "wording": w, "run_id": tid, "symptom": p["symptom"],
                              "group": symptoms[p["symptom"]]["group"], "category": p["category"],
                              "hub": p["hub"], "fault": p["fault"], "truth": p["truth"],
                              "verdict": v, "outcome": row["outcome"]}
            score = scored.get(answer_id, {})
            for field, value in expected_score.items():
                if score.get(field) != value:
                    errors.append(f"{answer_id} {field}: exported={value!r}, score={score.get(field)!r}")
        check(label + " row-by-row score and answer consistency", errors, [])
        comparisons.append((system, run, Counter(r["outcome"] for r in scores)))
    order = {sr: n for n, sr in enumerate(RUNS)}
    results.sort(key=lambda r: (qsort(r["item_id"].split("__")[0]), r["item_id"].split("__")[1],
                                r["wording"], order[r["system"], r["run"]]))
    check("Total result rows", len(results), 3612)
    unique(results, lambda r: (r["item_id"], r["wording"], r["system"], r["run"]), "result")
    sheets = [("Items", ITEM_FIELDS, items), ("Symptoms", SYMPTOM_FIELDS, symptom_rows),
              ("Programs", PROGRAM_FIELDS, program_rows), ("Traces", TRACE_FIELDS, trace_rows),
              ("Results", RESULT_FIELDS, results)]
    for name, fields, rows in sheets:
        csv_file(name.lower() + ".csv", fields, rows)
    jsonl_file("items.jsonl", items)
    jsonl_file("results.jsonl", results)
    # Reconcile the actual exported CSV, not just its in-memory precursor.
    with (HERE / "results.csv").open(encoding="utf-8", newline="") as f:
        exported = list(csv.DictReader(f))
    outcome_rows = []
    all_outcomes = sorted({r["outcome"] for r in exported} | {o for _, _, c in comparisons for o in c})
    for system, run, source_counts in comparisons:
        rows = [r for r in exported if r["system"] == system and r["run"] == str(run)]
        counts = Counter(r["outcome"] for r in rows)
        check(f"{system} run {run} exported outcome counts", dict(sorted(counts.items())), dict(sorted(source_counts.items())))
        outcome_rows.append([system, run, len(rows), *[counts[o] for o in all_outcomes],
                             "PASS" if counts == source_counts else "FAIL"])
    composition(items, [q for q in qs if q["wording"] == "precise"])
    documents(catalog["event_groups"])
    notes = [dict(topic=k, description=v) for k, v in [
        ("TraceSymptoms", "Natural-language questions about Linux kernel traces, with positive cases and negative controls."),
        ("Composition", "258 items; 56 questions in two wordings; 48 symptoms; 53 scenarios across nine programs; 56 traces."),
        ("Results", "3,612 verdict records: TraceAssist runs 1–3; Codex, TMLL, LLM only and RAG run 1. Full answers are in results.jsonl."),
        ("Keys", "item_id = question_id__trace_id. Results wording a is precise; b is everyday. Run means system repetition."),
        ("Lists and blanks", "Lists are JSON array text; empty lists are blank. Expected fields are populated only for present pairs. Numeric tolerances are preserved as text."),
        ("Scoring", "Truth: present / absent / cannot_see. Verdict: present / absent / cannot_tell. FN_cautious counts as FN; TN_abstain as TN. Unseeable cases are separate."),
        ("Trace metadata", "Duration is configured (30s), not measured. Event columns name groups. mem probes were unavailable on all traces; intentional omissions are separate."),
        ("Source and rebuild", "Read-only ../repo/bench JSON, capture metadata and saved results. Run python3 build_dataset.py. See README.md for field definitions and CHECKS.md for validation."),
        ("Use", "Give systems only a question and trace; withhold labels, fault metadata, expected answers and saved answers."),
        ("Licence / citation", "TBD / TBD. See DATASET_CARD.md.")]]
    xlsx = workbook_bytes(sheets, notes)
    (HERE / "TraceSymptoms.xlsx").write_bytes(xlsx)
    check("Workbook deterministic serialization", hashlib.sha256(xlsx).hexdigest(),
          hashlib.sha256(workbook_bytes(sheets, notes)).hexdigest())
    from openpyxl import load_workbook
    wb = load_workbook(HERE / "TraceSymptoms.xlsx")
    workbook_errors = []
    check("Workbook sheets", wb.sheetnames, ["README", "Items", "Symptoms", "Programs", "Traces", "Results"])
    for name, fields, rows in [("README", ["topic", "description"], notes)] + sheets:
        ws = wb[name]
        actual_rows = list(ws.values)
        wanted = [tuple(fields)] + [tuple(r[f] if r[f] != "" else None for f in fields) for r in rows]
        if actual_rows != wanted:
            workbook_errors.append(name + ": cell contents differ from table")
        if ws.freeze_panes not in ["A2", "B2"] or not all(c.alignment.wrap_text for row in ws for c in row):
            workbook_errors.append(name + ": missing frozen header or wrapping")
    check("Workbook round-trip data and formatting", workbook_errors, [])
    check("All traces report unavailable mem probes", [c["run_id"] for c in captures if c["events_unavailable"] != ["mem"]], [])
    changed = [name for name, digest in SOURCE_HASHES.items() if hashlib.sha256((REPO / name).read_bytes()).hexdigest() != digest]
    check("Consumed source files unchanged during build", changed, [])
    manifest = "".join(f"{name}\t{digest}\n" for name, digest in sorted(SOURCE_HASHES.items()))
    manifest_hash = hashlib.sha256(manifest.encode()).hexdigest()
    failures = [(n, a, e) for n, ok, a, e in CHECKS if not ok]
    lines = ["# TraceSymptoms checks\n", f"{'PASS' if not failures else 'FAIL'}: {len(CHECKS) - len(failures)} of {len(CHECKS)} checks passed.\n",
             "## Required composition\n", table(["Check", "Actual", "Expected", "Status"],
                [[n, a, e, "PASS" if ok else "FAIL"] for n, ok, a, e in CHECKS[:14]]),
             "## Outcome counts in results.csv\n", "Compared independently with each source run<N>_scores.csv. "
             "Each run also passes row-by-row identity, truth, verdict and outcome checks unless listed below.\n",
             table(["system", "run", "answers", *all_outcomes, "matches source"], outcome_rows),
             "## Mismatches\n"]
    if failures:
        for name, actual, expected in failures:
            lines += [f"- **{name}**: actual `{actual!r}`; expected `{expected!r}`."]
    else:
        lines.append("None. All requested counts and all seven system/run outcome distributions match the source.\n")
    lines += ["\n## Additional checks\n", *[f"- {'PASS' if ok else 'FAIL'}: {name}." for name, ok, _, _ in CHECKS[14:]],
              "\n## Interpretation notes\n",
              "- 53 scenario rows represent nine programs; three extra recordings make 56 traces.",
              "- All traces have configured duration 30s. Actual trace spans are not measured by this exporter.",
              "- Six cannot_see pairs: three memory-pressure pairs, two busy-waiting pairs, one crash without signals. "
              "The three event-omission recordings do not map one-to-one to these six pairs.",
              "- The source pair generator checks unavailable required events before don't-care labels. "
              "Q13 on cachesvc-48be is therefore cannot_see although the allocation_churn scenario lists "
              "memory_pressure as don't-care. This is a source-defined precedence rule, not a label changed by this exporter.",
              "- Outcome counts retain abstentions and unseeable outcomes; they are not silently folded into TP/FP/TN/FN.",
              "- Array fields preserve original list elements, including numeric tolerance text. Full answers are unchanged in JSONL.",
              "\n## Source fingerprint\n",
              f"Read and SHA-256 checked {len(SOURCE_HASHES)} source files. The sorted manifest "
              "uses `relative_path<TAB>sha256<LF>`; paths are relative to ../repo. Its SHA-256 is " + f"`{manifest_hash}`.\n",
              "The source files are opened only for reading. No source generator, scorer or module is executed. "
              "Documentation inputs include the paper's bench, threats and introduction sections and capture.sh "
              "to substantiate collection details.\n",
              "Core input fingerprints:\n",
              table(["Source", "SHA-256"], [[name, SOURCE_HASHES[name]] for name in
                    ["bench/questions.json", "bench/pairs.json", "bench/answer_key.json", "bench/symptoms.json",
                     "bench/scenarios.json", "bench/runs/index.csv"]])]
    text_file("CHECKS.md", "\n".join(lines))
    print("Built " + ", ".join(OUTPUTS))
    print(f"{len(items)} items; {len(symptom_rows)} symptoms; {len(program_rows)} scenarios; "
          f"{len(trace_rows)} traces; {len(results)} results.")
    print(f"Checks: {len(CHECKS) - len(failures)}/{len(CHECKS)} passed; {len(failures)} mismatches.")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        text_file("CHECKS.md", f"# TraceSymptoms checks\n\nFAIL: build could not complete.\n\n"
                  f"{type(exc).__name__}: {exc}\n\nOutputs may be incomplete; rerun after resolving this error.\n")
        raise

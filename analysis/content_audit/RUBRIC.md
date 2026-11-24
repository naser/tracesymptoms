# Content-audit rubric (fixed before grading)

You grade answers to questions about Linux kernel traces. Each item has the question, a summary of the
fault that was injected, and the answer key ("expected": where_any = at least one of these threads or
processes must be named as responsible; where_all = all of these must be named; cause; numbers with
tolerance; fix_any = acceptable fixes, only for remediation questions). Each item has two answers, A and B,
from two different systems. Grade each answer on its own, against the key only.

For each answer give:
- verdict: what the first line says (yes / no / cannot tell).
- location: correct | partly | wrong | missing — does it name the threads/processes in where_any / where_all
  as the ones responsible? (partly = names some of where_all, or names the right one among wrong ones as equals)
- cause: correct | partly | wrong | missing — does it give the expected cause (same mechanism; wording may differ)?
- numbers: correct | partly | wrong | missing | n/a — are the key's numbers stated within the tolerance?
  (n/a only if the key lists no numbers; partly = some right, some wrong or missing)
- fix: correct | wrong | missing | n/a — for keys with fix_any, does it propose an acceptable fix?
- overall: full (every applicable field correct) | partial (location correct, something else not) | wrong
- note: one short sentence explaining the main deduction.
Judge substance, not style. Do not reward length. If the answer says "no" or "cannot tell", grade what it
says anyway (usually location/cause missing).
Output: a JSON list, one object per item: {"item": ..., "A": {...}, "B": {...}}.

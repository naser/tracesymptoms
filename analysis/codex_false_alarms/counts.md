
## codex: 113 FPs
| category | n | % | self-contradicting | label-debatable |
|---|---:|---:|---:|---:|
| SCALE | 50 | 44% | 21 | 9 |
| THRESHOLD | 4 | 4% | 4 | 0 |
| INTERPRETATION | 32 | 28% | 9 | 0 |
| ADJACENT | 17 | 15% | 5 | 9 |
| LITERAL_TRUE | 4 | 4% | 0 | 4 |
| WRONG_ENTITY | 3 | 3% | 1 | 0 |
| MISMEASURED | 3 | 3% | 0 | 0 |
| all | 113 | 100% | 40 | 22 |

codex: category x wording (a=precise, b=everyday)
| category | a | b | total |
|---|---:|---:|---:|
| SCALE | 14 | 36 | 50 |
| THRESHOLD | 4 | 0 | 4 |
| INTERPRETATION | 13 | 19 | 32 |
| ADJACENT | 3 | 14 | 17 |
| LITERAL_TRUE | 0 | 4 | 4 |
| WRONG_ENTITY | 0 | 3 | 3 |
| MISMEASURED | 3 | 0 | 3 |
| total | 37 | 76 | 113 |

codex: category x symptom group
| category | cpu | lifecycle | pipelines | syscalls_io | timing | unexpected | waiting | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SCALE | 15 | 3 | 0 | 11 | 5 | 10 | 6 | 50 |
| THRESHOLD | 0 | 2 | 0 | 0 | 1 | 0 | 1 | 4 |
| INTERPRETATION | 2 | 3 | 5 | 1 | 0 | 10 | 11 | 32 |
| ADJACENT | 2 | 0 | 0 | 6 | 5 | 0 | 4 | 17 |
| LITERAL_TRUE | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 4 |
| WRONG_ENTITY | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 3 |
| MISMEASURED | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 3 |
| total | 20 | 8 | 5 | 19 | 14 | 21 | 26 | 113 |

codex: FPs on healthy (fault none) traces: SCALE=22, THRESHOLD=2, INTERPRETATION=15, LITERAL_TRUE=1, WRONG_ENTITY=2 (total 42)

## traceassist: 24 FPs
| category | n | % | self-contradicting | label-debatable |
|---|---:|---:|---:|---:|
| SCALE | 6 | 25% | 6 | 0 |
| INTERPRETATION | 2 | 8% | 1 | 0 |
| ADJACENT | 12 | 50% | 7 | 10 |
| LITERAL_TRUE | 4 | 17% | 0 | 4 |
| all | 24 | 100% | 14 | 14 |

traceassist: category x wording (a=precise, b=everyday)
| category | a | b | total |
|---|---:|---:|---:|
| SCALE | 3 | 3 | 6 |
| INTERPRETATION | 1 | 1 | 2 |
| ADJACENT | 2 | 10 | 12 |
| LITERAL_TRUE | 0 | 4 | 4 |
| total | 6 | 18 | 24 |

traceassist: category x symptom group
| category | cpu | lifecycle | syscalls_io | timing | unexpected | waiting | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| SCALE | 3 | 2 | 0 | 0 | 0 | 1 | 6 |
| INTERPRETATION | 0 | 0 | 0 | 0 | 0 | 2 | 2 |
| ADJACENT | 2 | 0 | 1 | 2 | 2 | 5 | 12 |
| LITERAL_TRUE | 0 | 0 | 0 | 0 | 0 | 4 | 4 |
| total | 5 | 2 | 1 | 2 | 2 | 12 | 24 |

traceassist: FPs on healthy (fault none) traces: SCALE=2, INTERPRETATION=1, LITERAL_TRUE=1 (total 4)

## Overlap (same question, wording and trace)
Codex FP -> TraceAssist outcome: {'TN_abstain': 4, 'TN': 93, 'FP': 16}
By Codex category, TraceAssist TN count:
  SCALE: 46/50 TraceAssist TN or TN_abstain; strict TN 46
  THRESHOLD: 4/4 TraceAssist TN or TN_abstain; strict TN 3
  INTERPRETATION: 31/32 TraceAssist TN or TN_abstain; strict TN 30
  ADJACENT: 10/17 TraceAssist TN or TN_abstain; strict TN 8
  LITERAL_TRUE: 0/4 TraceAssist TN or TN_abstain; strict TN 0
  WRONG_ENTITY: 3/3 TraceAssist TN or TN_abstain; strict TN 3
  MISMEASURED: 3/3 TraceAssist TN or TN_abstain; strict TN 3
TraceAssist FP -> Codex outcome: {'FP': 16, 'TN': 5, 'TN_abstain': 3}

## Codex effort, TP vs FP (medians)
| outcome | n | median n_commands | median elapsed_s | median output_tokens |
|---|---:|---:|---:|---:|
| TP | 134 | 16.0 | 218 | 11655.5 |
| FP | 113 | 16 | 221 | 11498 |
| TN | 209 | 16 | 210 | 11287 |
| FN | 8 | 15.5 | 226 | 16591.5 |
| FP:SCALE | 50 | 15.0 | 172 | 9413.0 |
| FP:THRESHOLD | 4 | 13.5 | 226 | 10992.0 |
| FP:INTERPRETATION | 32 | 17.0 | 259 | 12398.5 |
| FP:ADJACENT | 17 | 18 | 256 | 13293 |
| FP:LITERAL_TRUE | 4 | 15.5 | 191 | 10938.5 |
| FP:WRONG_ENTITY | 3 | 14 | 333 | 11950 |
| FP:MISMEASURED | 3 | 24 | 330 | 17067 |
| TP on question-wordings that also have an FP | 70 | 15.0 | 205 | 11142.0 |
Mann-Whitney TP vs FP on n_commands: p = 0.984
Mann-Whitney TP vs FP on elapsed_s: p = 0.746
codex outcomes: {'TN': 209, 'FP': 113, 'TN_abstain': 34, 'TP': 134, 'correct_unseeable': 10, 'FN': 8, 'FN_cautious': 6, 'FP_unseeable': 1, 'wrong_unseeable': 1}
traceassist outcomes: {'TN': 319, 'TN_abstain': 13, 'TP': 137, 'FP': 24, 'correct_unseeable': 12, 'FN_cautious': 1, 'FN': 10}

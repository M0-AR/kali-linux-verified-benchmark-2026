# Extended paper draft (companion to README — README is canonical)

This file holds the PhD-submission scaffolding: problem statement refinement,
related-work deltas, and the three hypotheses in testable form. All numbers
are imported from `results/*.json` — never hand-edited.

## Problem statement (1 paragraph for the committee)

Beginner offensive-security texts decay unevenly and no reproducible harness
exists to tell teachers *what* still verifies, *what* is superseded, and
*what* is unsafe to teach as written. We close that gap for one widely
circulated corpus with a Docker artifact + live-grounded audit.

## Related-work positioning

- KaliBench (2026) benchmarks NL→CLI but does not audit pedagogy; we reuse
  its metric (exact-command, alias-aware) as our teaching endpoint.
- AutoPenBench/PentestAgent/ADAPT benchmark agents end-to-end (21% auto);
  we benchmark *humans-through-frameworks* (59/63/49) — complementary.
- JAIC 2025 compares frameworks on shared targets; we add Wilson CIs,
  $/finding, and a Docker rerun harness.
- pwnkit methodology contributes the reporting discipline (substrate + CI +
  cost) we enforce.

## Hypotheses (falsifiable)

H1 (Half-Life Gradient): plumbing-naming claims decay ~10× faster than
primitive claims. Test: logistic regression accuracy ~ plumbing_ratio.

H2 (Trilemma stability): OWASP-fast / PTES-deep / NIST-governable ordering
persists under continuous-testing arms. Test: JAIC rerun + NodeZero arm.

H3 (Argument bottleneck): docs-first teaching raises exact-command rate
>15pp over tool-first on Juice Shop. Test: RCT, KaliBench hinted metric.

## Ethics appendix

Rules of Engagement template, authorization checklist, and lab-isolation
proof (`docker network inspect ... isolated-lab -- internal:true`) belong
here in the submission. No offensive output is stored in this repo.

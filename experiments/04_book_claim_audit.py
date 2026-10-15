"""Experiment 04 — Book-claim audit (Jason Knox 'Computer Hacking 2 Books in 1').

Method: each row in data/book_claims.csv states a verifiable factual claim
from the book text (chapter-scoped), the 2026 ground truth established by
this study's online verification (Oct 2026), and a verdict:

  CONFIRMED  — still true in 2026
  OUTDATED   — true at publication (~2018-2019) but superseded
  DEPRECATED — actively discouraged / removed in modern practice
  UNSAFE     — true technically but must only be done with explicit
               authorization in an isolated lab (ethics gate)

This script recomputes the tally, prints the table, and writes
results/exp04.json. It performs NO hacking techniques — it audits TEXTUAL
accuracy against live documentation (Kali releases, Debian, NIST, OWASP).
That is the publishable contribution: a reproducible errata + modernization
map from a 2019-era book to 2026 best practice.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CSV = BASE / "data" / "book_claims.csv"


def main():
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    counts = Counter(r["verdict"].strip().upper() for r in rows)
    print(f"{'ID':<6}{'Verdict':<11}Claim (short)")
    print("-" * 90)
    for r in rows:
        print(f"{r['id']:<6}{r['verdict'].strip().upper():<11}{r['claim_short'][:72]}")
    print("-" * 90)
    total = len(rows)
    for k in ["CONFIRMED", "OUTDATED", "DEPRECATED", "UNSAFE"]:
        print(f"  {k:<11}: {counts.get(k,0):>2}  ({counts.get(k,0)/total*100:4.1f}%)")
    outdated_share = (counts.get("OUTDATED", 0) + counts.get("DEPRECATED", 0)) / total * 100
    finding = (f"{outdated_share:.0f}% of sampled book claims are OUTDATED/DEPRECATED in Oct 2026. "
               "Core Linux concepts (FHS, rwx, pipes) CONFIRMED; tooling/workflow (Kali 1.0.5, "
               "ifconfig, WEP-era wireless, VirtualBox-only lab, fish-as-default) superseded by "
               "Kali 2026.x + Docker/Exegol + WPA3 + NIST/PTES/OWASP hybrid. "
               "Offensive steps reclassified UNSAFE without written authorization.")
    print("\nFINDING: " + finding)
    out = {"experiment": "04_book_claim_audit", "total_claims": total,
           "tally": dict(counts), "outdated_deprecated_pct": round(outdated_share, 1),
           "finding": finding, "rows": rows}
    outp = BASE / "results" / "exp04.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n04 done -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

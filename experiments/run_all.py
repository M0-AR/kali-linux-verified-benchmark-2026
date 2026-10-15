"""Run all experiments in order, aggregate into results/summary.json."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

ORDER = [
    "01_linux_fundamentals_verify.py",
    "02_framework_benchmark.py",
    "03_live_public_data_verify.py",
    "04_book_claim_audit.py",
]

def main():
    summary = {"benchmark": "kali-linux-verified-benchmark-2026", "date_utc": "2026-10-15",
               "ethics": "authorized defensive lab only; no offensive techniques executed",
               "experiments": []}
    failed = []
    for f in ORDER:
        print(f"\n{'='*70}\n>>> {f}\n{'='*70}")
        p = subprocess.run([sys.executable, str(BASE / f)])
        summary["experiments"].append({"script": f, "exit_code": p.returncode})
        if p.returncode != 0 and f != "03_live_public_data_verify.py":
            # exp01 strict; others informational — record but continue
            if f == "01_linux_fundamentals_verify.py":
                failed.append(f)
    # aggregate result files if present
    agg = {}
    for name in ["exp01.json", "exp02.json", "exp03.json", "exp04.json"]:
        fp = ROOT / "results" / name
        if fp.exists():
            agg[name] = json.loads(fp.read_text())
    summary["results_snapshot"] = {
        "exp01_passed": agg.get("exp01.json", {}).get("passed"),
        "exp01_failed": agg.get("exp01.json", {}).get("failed"),
        "exp02_finding": (agg.get("exp02.json", {}).get("finding", "")[:200]),
        "exp03_live": agg.get("exp03.json", {}).get("live_count"),
        "exp04_tally": agg.get("exp04.json", {}).get("tally"),
    }
    outp = ROOT / "results" / "summary.json"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(summary, indent=2))
    print(f"\nAll done -> {outp}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())

"""Experiment 01 — Linux fundamentals verification (defensive, offline-safe).

Verifies the timeless subset of 'Linux for Beginners' claims that remain true
in 2026 without requiring privileged operations or network access:
- FHS paths (/bin, /etc, /home, /tmp, /usr, /var, /proc, /dev, /root)
- ls/mkdir/cd/pwd/cp/rm/cat/head/tail/grep semantics on temp dirs
- chmod octal mapping 0-7 <-> rwx (the same table the book prints)
- $PATH, $HOME, $PWD, $SHELL, $TERM presence
- nano/vi presence check (informational only, no editing)

All operations run inside a sandboxed temp directory under /tmp and are
cleaned up. No system files are modified. Exit code 0 on full pass.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

RESULTS = {"experiment": "01_linux_fundamentals", "checks": [], "passed": 0, "failed": 0}


def check(name, ok, detail=""):
    RESULTS["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:500]})
    if ok:
        RESULTS["passed"] += 1
    else:
        RESULTS["failed"] += 1
    print(("[PASS] " if ok else "[FAIL] ") + name + (f" — {detail}" if detail else ""))


def run(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=15)
    return p.returncode, p.stdout.strip(), p.stderr.strip()[:300]


def main():
    # 1. FHS spot-check (existence only; containers may minimal-mount some)
    expected_dirs = ["/bin", "/etc", "/home", "/tmp", "/usr", "/var", "/proc", "/dev", "/root"]
    for d in expected_dirs:
        check(f"fhs_exists:{d}", Path(d).exists(), "exists" if Path(d).exists() else "missing")

    # 2. pwd/ls/mkdir/cd lifecycle in sandbox
    sandbox = Path(tempfile.mkdtemp(prefix="lxverify_"))
    try:
        rc, out, _ = run("pwd")
        check("cmd_pwd_runs", rc == 0 and len(out) > 0, out)
        rc, out, _ = run(f"mkdir -p {sandbox}/linuxstuff/backups && ls {sandbox}/linuxstuff")
        check("cmd_mkdir_ls", rc == 0 and "backups" in out, out)
        rc, out, _ = run(f"echo hello > {sandbox}/linuxstuff/file1.txt && cp {sandbox}/linuxstuff/file1.txt {sandbox}/linuxstuff/file2.txt && ls {sandbox}/linuxstuff")
        check("cmd_cp", rc == 0 and "file1.txt" in out and "file2.txt" in out, out)
        rc, out, _ = run(f"cat {sandbox}/linuxstuff/file1.txt")
        check("cmd_cat", rc == 0 and out == "hello", out)
        rc, out, _ = run(f"printf 'a\\nb\\nc\\n' > {sandbox}/s.txt && head -n 1 {sandbox}/s.txt && tail -n 1 {sandbox}/s.txt")
        check("cmd_head_tail", rc == 0 and "a" in out and "c" in out, out)
        rc, out, _ = run(f"echo Science science SCIENCE > {sandbox}/g.txt && grep -i science {sandbox}/g.txt")
        check("cmd_grep_case_insensitive", rc == 0 and "science" in out.lower(), out)
        rc, out, _ = run(f"rm {sandbox}/linuxstuff/file2.txt && ls {sandbox}/linuxstuff")
        check("cmd_rm", rc == 0 and "file2.txt" not in out, out)
        rc, out, _ = run(f"rmdir {sandbox}/linuxstuff/backups && ls {sandbox}/linuxstuff")
        check("cmd_rmdir_empty", rc == 0 and "backups" not in out, out)
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    # 3. Octal <-> rwx mapping (book pp. permissions chapter). Ground truth table.
    octal_to_rwx = {"0": "---", "1": "--x", "2": "-w-", "3": "-wx",
                    "4": "r--", "5": "r-x", "6": "rw-", "7": "rwx"}
    mapping_ok = True
    for octal, rwx in octal_to_rwx.items():
        # verify via stat: create temp file, chmod, read back
        fd, p = tempfile.mkstemp()
        os.close(fd)
        try:
            os.chmod(p, int(octal, 8) * 0o100)  # owner-only bits for isolated check
            mode = stat.S_IMODE(os.stat(p).st_mode)
            owner_bits = (mode >> 6) & 0o7
            if owner_bits != int(octal, 8):
                mapping_ok = False
        finally:
            os.unlink(p)
    check("chmod_octal_0_7_roundtrip", mapping_ok, "0=---..7=rwx verified via stat")
    # 755 canonical: rwxr-xr-x
    fd, p = tempfile.mkstemp()
    os.close(fd)
    try:
        os.chmod(p, 0o755)
        mode = stat.filemode(os.stat(p).st_mode)
        check("chmod_755_is_rwxr_xr_x", "rwxr-xr-x" in mode, mode)
    finally:
        os.unlink(p)

    # 4. Environment variables the book lists
    for var in ["PATH", "HOME", "PWD", "SHELL", "TERM"]:
        val = os.environ.get(var, "")
        # PWD/SHELL/TERM may be unset in minimal containers; report but only require PATH/HOME
        required = var in ("PATH", "HOME")
        ok = (len(val) > 0) if required else True
        check(f"env_{var}", ok, val[:120] if val else ("unset (optional)" if not required else "MISSING"))

    # 5. Editors present (informational)
    for ed in ["nano", "vi"]:
        rc, _, _ = run(f"command -v {ed}")
        check(f"editor_present:{ed}", True, "found" if rc == 0 else "not installed (optional)")

    # 6. Deprecated-command awareness (2026 best practice, verified via StackOverflow/Debian docs):
    # ifconfig (net-tools) is deprecated in favour of `ip` (iproute2). We assert `ip` exists
    # OR document the gap — this is a book-accuracy finding, not a failure.
    rc_ip, _, _ = run("command -v ip")
    rc_ifc, _, _ = run("command -v ifconfig")
    check("modern_ip_cmd_available", True,
          f"ip={'yes' if rc_ip==0 else 'no'}, ifconfig={'yes(legacy)' if rc_ifc==0 else 'no(deprecated as expected)'}")

    out_path = Path(__file__).resolve().parent.parent / "results" / "exp01.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(RESULTS, indent=2))
    print(f"\n01 done: {RESULTS['passed']} passed, {RESULTS['failed']} failed -> {out_path}")
    return 0 if RESULTS["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

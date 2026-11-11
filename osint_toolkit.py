#!/usr/bin/env python3
"""
osint_toolkit.py - run common open-source OSINT tools from one command
and save the output to a single report folder.

For authorized or lawful use only (your own footprint, pentests with written
scope, due diligence). You must pass --authorized to confirm this.

Examples:
  python osint_toolkit.py --authorized --email you@example.com
  python osint_toolkit.py --authorized --username johndoe --phone +919876543210
  python osint_toolkit.py --authorized --name "John Doe" --email john@example.com
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

# Make tools findable on Kali, Termux and Docker without activating the venv.
_HERE = Path(__file__).resolve().parent
for _d in (_HERE / "venv" / "bin", _HERE / "bin"):
    if _d.is_dir():
        os.environ["PATH"] = str(_d) + os.pathsep + os.environ.get("PATH", "")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+\d{7,15}$")


def run_tool(label, cmd, outdir, timeout=300):
    """Run one tool, save stdout/stderr to a file, return a status line."""
    exe = cmd[0]
    if shutil.which(exe) is None:
        return f"[SKIP] {label}: '{exe}' not installed (run setup.sh)"
    logfile = outdir / f"{label}.txt"
    print(f"[*] Running {label} ...")
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=outdir
        )
        logfile.write_text(
            f"$ {' '.join(cmd)}\n\n{proc.stdout}\n{proc.stderr}", encoding="utf-8"
        )
        status = "OK" if proc.returncode == 0 else f"EXIT {proc.returncode}"
        return f"[{status}] {label} -> {logfile.name}"
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] {label} after {timeout}s"
    except Exception as exc:  # keep going if one tool breaks
        return f"[ERROR] {label}: {exc}"


def dork_links(name, email=None):
    """Build search URLs to open manually. Nothing is scraped."""
    queries = {
        "general": f'"{name}"',
        "linkedin": f'"{name}" site:linkedin.com',
        "github": f'"{name}" site:github.com',
        "twitter_x": f'"{name}" site:x.com OR site:twitter.com',
        "pdf_docs": f'"{name}" filetype:pdf',
    }
    if email:
        queries["email_mentions"] = f'"{email}"'
    return {
        k: "https://www.google.com/search?q=" + urllib.parse.quote(v)
        for k, v in queries.items()
    }


def main():
    p = argparse.ArgumentParser(description="Run OSINT tools and collect results.")
    p.add_argument("--email")
    p.add_argument("--phone", help="international format, e.g. +919876543210")
    p.add_argument("--username")
    p.add_argument("--name", help="full name (generates search links)")
    p.add_argument("--timeout", type=int, default=300, help="per-tool timeout (s)")
    p.add_argument(
        "--authorized",
        action="store_true",
        help="confirm you have a lawful basis / permission for this lookup",
    )
    args = p.parse_args()

    if not args.authorized:
        sys.exit("Refusing to run: pass --authorized to confirm lawful, "
                 "permitted use (own data, written scope, due diligence).")
    if not any([args.email, args.phone, args.username, args.name]):
        p.error("give at least one of --email, --phone, --username, --name")
    if args.email and not EMAIL_RE.match(args.email):
        p.error("invalid email format")
    if args.phone and not PHONE_RE.match(args.phone):
        p.error("phone must be like +919876543210")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir = Path("results") / stamp
    outdir.mkdir(parents=True, exist_ok=True)
    summary = [f"OSINT run {stamp}", "=" * 40]

    if args.email:
        summary.append(run_tool(
            "holehe", ["holehe", "--only-used", "--no-color", args.email],
            outdir, args.timeout))
        summary.append(run_tool(
            "h8mail", ["h8mail", "-t", args.email], outdir, args.timeout))

    if args.phone:
        summary.append(run_tool(
            "phoneinfoga", ["phoneinfoga", "scan", "-n", args.phone],
            outdir, args.timeout))

    if args.username:
        summary.append(run_tool(
            "sherlock",
            ["sherlock", args.username, "--print-found", "--timeout", "10",
             "--folderoutput", str(outdir.resolve())],
            outdir, args.timeout))
        summary.append(run_tool(
            "maigret",
            ["maigret", args.username, "--timeout", "10",
             "--folderoutput", str(outdir.resolve())],
            outdir, args.timeout))

    if args.name:
        links = dork_links(args.name, args.email)
        lines = [f"{k}: {v}" for k, v in links.items()]
        (outdir / "search_links.txt").write_text("\n".join(lines), encoding="utf-8")
        summary.append("[OK] search links -> search_links.txt")

    report = outdir / "SUMMARY.txt"
    report.write_text("\n".join(summary), encoding="utf-8")
    print("\n" + "\n".join(summary))
    print(f"\nResults saved in: {outdir}")
    print("Reminder: results are leads, not proof. Verify before acting on them.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ReconAI - Main Orchestrator
by @0xnhsec

Usage:
  python3 recon.py <target> [--phase 1|2|3|all]
"""

import sys, os, json, argparse
from datetime import datetime

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
CYAN="\033[96m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"

BANNER = r"""
███████╗███████╗ ██████╗ ██████╗ ███╗   ██╗ █████╗ ██╗
██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║██╔══██╗██║
██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║███████║██║
██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║██╔══██║██║
██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║██║  ██║██║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝
AI-Assisted Recon Framework                      @0xnhsec
"""
SEP = "─" * 60

def log(msg, level="info"):
    icons = {"info":f"{CYAN}[*]{RESET}","ok":f"{GREEN}[+]{RESET}",
             "warn":f"{YELLOW}[!]{RESET}","err":f"{RED}[x]{RESET}"}
    print(f"  {icons.get(level,'[?]')} {msg}")

def check_scope():
    """Read and validate SCOPE.md before any scan."""
    scope_file = os.path.join(os.path.dirname(__file__), "SCOPE.md")
    if not os.path.exists(scope_file):
        log("SCOPE.md not found!", "err")
        log("Create and fill SCOPE.md before scanning", "warn")
        sys.exit(1)
    with open(scope_file) as f:
        content = f.read()
    # Check if target field is filled
    if "Domain  : \n" in content or "Domain  :\n" in content:
        log("SCOPE.md is not filled — Domain field is empty", "err")
        log("Fill in SCOPE.md before proceeding", "warn")
        sys.exit(1)
    log("SCOPE.md validated", "ok")
    return content

def merge_json_output(outdir, target):
    """Merge all phase outputs into single recon.json for Phase 4."""
    merged = {
        "meta": {
            "framework": "ReconAI by @0xnhsec",
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "ready_for_phase4": True
        }
    }
    for phase_file in ["phase1_assets.json", "phase2_live.json", "phase3_fingerprint.json"]:
        fpath = os.path.join(outdir, phase_file)
        if os.path.exists(fpath):
            with open(fpath) as f:
                key = phase_file.replace(".json","")
                merged[key] = json.load(f)
        else:
            log(f"{phase_file} not found — skipped in merge", "warn")

    merged_file = os.path.join(outdir, "recon_full.json")
    with open(merged_file, "w") as f:
        json.dump(merged, f, indent=2)

    log(f"Merged output → {merged_file}", "ok")
    log("Feed recon_full.json to Claude using CLAUDE_PHASE4_PROMPT.md", "info")
    return merged_file

def main():
    print(CYAN + BANNER + RESET)
    print(SEP)

    parser = argparse.ArgumentParser(
        prog="recon",
        description="ReconAI — AI-assisted recon framework by @0xnhsec"
    )
    parser.add_argument("target",  help="Target domain (e.g. juice-shop.herokuapp.com)")
    parser.add_argument("--phase", default="all",
                        choices=["1","2","3","all","merge"],
                        help="Phase to run (default: all)")
    args = parser.parse_args()

    target = args.target.replace("https://","").replace("http://","").rstrip("/")
    outdir = os.path.join(os.path.dirname(__file__), "output", target)
    os.makedirs(outdir, exist_ok=True)

    log(f"Target : {BOLD}{target}{RESET}")
    log(f"Phase  : {args.phase}")
    log(f"Output : {outdir}")
    print()

    # Scope check — always
    check_scope()
    print()

    # Import runners
    sys.path.insert(0, os.path.dirname(__file__))

    if args.phase in ("1", "all"):
        print(SEP)
        from phase1.runner import run as p1
        p1(target, outdir)

    if args.phase in ("2", "all"):
        print(SEP)
        from phase2.runner import run as p2
        p2(target, outdir)

    if args.phase in ("3", "all"):
        print(SEP)
        from phase3.runner import run as p3
        p3(target, outdir)

    if args.phase in ("all", "merge"):
        print(SEP)
        log("Merging all phase outputs...", "info")
        merge_json_output(outdir, target)

    print()
    print(SEP)
    log(f"Done. Output saved to: {outdir}", "ok")
    if args.phase in ("all", "merge"):
        log("Next: open CLAUDE_PHASE4_PROMPT.md and feed recon_full.json to Claude", "info")
    print()

if __name__ == "__main__":
    main()

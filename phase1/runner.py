#!/usr/bin/env python3
"""
ReconAI - Phase 1: Asset Discovery (Passive)
by @0xnhsec

Runs passive discovery tools, outputs phase1_assets.json
"""

import subprocess, json, sys, os, requests
from datetime import datetime

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
CYAN="\033[96m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"

def log(msg, level="info"):
    icons = {"info":f"{CYAN}[*]{RESET}","ok":f"{GREEN}[+]{RESET}",
             "warn":f"{YELLOW}[!]{RESET}","err":f"{RED}[x]{RESET}"}
    print(f"  {icons.get(level,'[?]')} {msg}")

def run_cmd(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except Exception:
        return "", -1

def check_tool(name):
    out, _ = run_cmd(f"which {name}")
    return bool(out)

def run_assetfinder(target):
    log(f"assetfinder → {target}")
    if not check_tool("assetfinder"):
        log("assetfinder not found — skipped", "warn")
        return [], "tool_not_found"
    out, _ = run_cmd(f"assetfinder --subs-only {target}", timeout=60)
    subs = [s.strip() for s in out.splitlines() if s.strip()]
    log(f"assetfinder: {len(subs)} subdomains", "ok")
    return subs, "ok"

def run_sublist3r(target, outdir):
    log(f"sublist3r → {target}")
    if not check_tool("sublist3r"):
        log("sublist3r not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "subs_sublist3r.txt")
    run_cmd(f"sublist3r -d {target} -o {outfile}", timeout=120)
    if os.path.exists(outfile):
        with open(outfile) as f:
            subs = [l.strip() for l in f if l.strip()]
        log(f"sublist3r: {len(subs)} subdomains", "ok")
        return subs, "ok"
    return [], "no_output"

def run_waybackurls(target):
    log(f"waybackurls → {target}")
    if not check_tool("waybackurls"):
        log("waybackurls not found — skipped", "warn")
        return [], "tool_not_found"
    out, _ = run_cmd(f"echo {target} | waybackurls", timeout=60)
    urls = [u.strip() for u in out.splitlines() if u.strip()]
    log(f"waybackurls: {len(urls)} URLs", "ok")
    return urls, "ok"

def run_crtsh(target):
    log(f"crt.sh → {target}")
    try:
        r = requests.get(f"https://crt.sh/?q=%.{target}&output=json", timeout=30)
        if r.status_code == 200:
            data = r.json()
            names = list(set(
                e["name_value"].replace("*.", "").strip()
                for e in data if "name_value" in e
            ))
            log(f"crt.sh: {len(names)} entries", "ok")
            return names, "ok"
    except Exception as e:
        log(f"crt.sh failed: {e}", "warn")
    return [], "failed"

def run(target, outdir):
    os.makedirs(outdir, exist_ok=True)
    print()
    print(f"  {BOLD}{CYAN}[ PHASE 1 — Asset Discovery (Passive) ]{RESET}")
    print(f"  {DIM}Target : {target}{RESET}")
    print(f"  {DIM}Output : {outdir}{RESET}\n")

    af_subs,  af_st  = run_assetfinder(target)
    sl_subs,  sl_st  = run_sublist3r(target, outdir)
    wb_urls,  wb_st  = run_waybackurls(target)
    crt_subs, crt_st = run_crtsh(target)

    all_subs = sorted(set(af_subs + sl_subs + crt_subs))
    if target not in all_subs:
        all_subs.append(target)
        all_subs.sort()
    
    log(f"Total unique subdomains: {len(all_subs)}", "ok")

    # Save raw list for phase2
    with open(os.path.join(outdir, "subs_all.txt"), "w") as f:
        f.write("\n".join(all_subs))

    output = {
        "meta": {
            "phase": 1,
            "phase_name": "asset_discovery",
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "output_dir": outdir
        },
        "tools_run": {
            "assetfinder": af_st,
            "sublist3r":   sl_st,
            "waybackurls": wb_st,
            "crt.sh":      crt_st
        },
        "subdomains": {
            "total": len(all_subs),
            "list": all_subs
        },
        "wayback_urls": {
            "total": len(wb_urls),
            "list": wb_urls[:300]
        },
        "ai_note": "Passive only — no direct target contact. All subdomains require live validation in Phase 2.",
        "next_phase": "Feed output/subs_all.txt to phase2/runner.py"
    }

    outfile = os.path.join(outdir, "phase1_assets.json")
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)

    print()
    log(f"Saved → {outfile}", "ok")
    return output

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 runner.py <target> <outdir>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])

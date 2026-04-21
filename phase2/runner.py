#!/usr/bin/env python3
"""
ReconAI - Phase 2: Live Validation (Active-light)
by @0xnhsec

Probes discovered subdomains, outputs phase2_live.json
"""

import subprocess, json, sys, os
from datetime import datetime

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
CYAN="\033[96m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"

def log(msg, level="info"):
    icons = {"info":f"{CYAN}[*]{RESET}","ok":f"{GREEN}[+]{RESET}",
             "warn":f"{YELLOW}[!]{RESET}","err":f"{RED}[x]{RESET}"}
    print(f"  {icons.get(level,'[?]')} {msg}")

def run_cmd(cmd, timeout=120):
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

def run_httprobe(subs_file, outdir):
    log("httprobe → checking live hosts")
    if not check_tool("httprobe"):
        log("httprobe not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "live_hosts.txt")
    run_cmd(f"cat {subs_file} | httprobe > {outfile}", timeout=180)
    if os.path.exists(outfile):
        with open(outfile) as f:
            hosts = [l.strip() for l in f if l.strip()]
        log(f"httprobe: {len(hosts)} live hosts", "ok")
        return hosts, "ok"
    return [], "no_output"

def run_httpx(subs_file, outdir):
    log("httpx → fingerprinting live hosts")
    if not check_tool("httpx"):
        log("httpx not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "httpx.json")
    run_cmd(
        f"httpx -l {subs_file} -json -sc -title -tech-detect -server -o {outfile}",
        timeout=300
    )
    results = []
    if os.path.exists(outfile):
        with open(outfile) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        results.append(json.loads(line))
                    except Exception:
                        pass
        log(f"httpx: {len(results)} hosts fingerprinted", "ok")
        return results, "ok"
    return [], "no_output"

def run_naabu(target, outdir):
    log(f"naabu → port scan {target}")
    if not check_tool("naabu"):
        log("naabu not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "ports.json")
    run_cmd(f"naabu -host {target} -json -o {outfile}", timeout=180)
    results = []
    if os.path.exists(outfile):
        with open(outfile) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        results.append(json.loads(line))
                    except Exception:
                        pass
        log(f"naabu: {len(results)} port results", "ok")
        return results, "ok"
    return [], "no_output"

def run_rustscan(target, outdir):
    log(f"rustscan → port scan {target}")
    if not check_tool("rustscan"):
        log("rustscan not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "rustscan.json")
    # Rustscan usually takes the domain/IP. We strip port if present for the -a flag.
    pure_target = target.split(":")[0]
    run_cmd(f"rustscan -a {pure_target} --json -o {outfile}", timeout=180)
    if os.path.exists(outfile):
        try:
            with open(outfile) as f:
                data = json.load(f)
            log("rustscan: port scan complete", "ok")
            return data, "ok"
        except Exception:
            pass
    return [], "no_output"

def parse_httpx_results(raw):
    """Normalize httpx JSON output into clean format."""
    parsed = []
    for h in raw:
        parsed.append({
            "host": h.get("input", ""),
            "url": h.get("url", ""),
            "status_code": h.get("status-code", 0),
            "title": h.get("title", ""),
            "tech": h.get("technologies", []),
            "server": h.get("webserver", ""),
            "ip": h.get("host", ""),
            "port": h.get("port", ""),
            "content_length": h.get("content-length", 0)
        })
    return parsed

def run(target, outdir, subs_file=None):
    os.makedirs(outdir, exist_ok=True)

    # Default subs file location
    if not subs_file:
        subs_file = os.path.join(outdir, "subs_all.txt")

    print()
    print(f"  {BOLD}{CYAN}[ PHASE 2 — Live Validation ]{RESET}")
    print(f"  {DIM}Target : {target}{RESET}")
    print(f"  {DIM}Subs   : {subs_file}{RESET}")
    print(f"  {DIM}Output : {outdir}{RESET}\n")

    if not os.path.exists(subs_file):
        log(f"Subs file not found: {subs_file}", "err")
        log("Run Phase 1 first or provide subs file path", "warn")
        sys.exit(1)

    hp_hosts,  hp_st  = run_httprobe(subs_file, outdir)
    hx_raw,    hx_st  = run_httpx(subs_file, outdir)
    nb_ports,  nb_st  = run_naabu(target, outdir)
    rs_ports,  rs_st  = run_rustscan(target, outdir)

    hx_parsed = parse_httpx_results(hx_raw)

    # Save live hosts for phase3
    live_file = os.path.join(outdir, "live_hosts.txt")
    if hx_parsed:
        with open(live_file, "w") as f:
            for h in hx_parsed:
                if h["url"]:
                    f.write(h["url"] + "\n")

    output = {
        "meta": {
            "phase": 2,
            "phase_name": "live_validation",
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "output_dir": outdir
        },
        "tools_run": {
            "httprobe": hp_st,
            "httpx":    hx_st,
            "naabu":    nb_st,
            "rustscan": rs_st
        },
        "live_hosts": {
            "total": len(hx_parsed),
            "hosts": hx_parsed
        },
        "open_ports": {
            "total": len(nb_ports),
            "results": nb_ports,
            "rustscan_raw": rs_ports
        },
        "ai_note": "All data verified by tools. Tech stack and status codes are tool-confirmed. Port results require service verification.",
        "next_phase": f"Feed {live_file} to phase3/runner.py"
    }

    outfile = os.path.join(outdir, "phase2_live.json")
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)

    log(f"Live hosts: {len(hx_parsed)}", "ok")
    log(f"Saved → {outfile}", "ok")
    return output

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 runner.py <target> <outdir> [subs_file]")
        sys.exit(1)
    subs = sys.argv[3] if len(sys.argv) > 3 else None
    run(sys.argv[1], sys.argv[2], subs)

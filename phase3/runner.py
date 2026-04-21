#!/usr/bin/env python3
"""
ReconAI - Phase 3: Deep Fingerprint & Crawl (Active)
by @0xnhsec

Crawls, extracts JS secrets, params, GraphQL, tech — outputs phase3_fingerprint.json
"""

import subprocess, json, sys, os, re
from datetime import datetime

RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"
CYAN="\033[96m"; BOLD="\033[1m"; DIM="\033[2m"; RESET="\033[0m"

def log(msg, level="info"):
    icons = {"info":f"{CYAN}[*]{RESET}","ok":f"{GREEN}[+]{RESET}",
             "warn":f"{YELLOW}[!]{RESET}","err":f"{RED}[x]{RESET}"}
    print(f"  {icons.get(level,'[?]')} {msg}")

def run_cmd(cmd, timeout=180):
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

def run_whatweb(target, outdir):
    log(f"whatweb → {target}")
    if not check_tool("whatweb"):
        log("whatweb not found — skipped", "warn")
        return {}, "tool_not_found"
    outfile = os.path.join(outdir, "whatweb.json")
    run_cmd(f"whatweb {target} --log-json={outfile}", timeout=60)
    if os.path.exists(outfile):
        try:
            with open(outfile) as f:
                data = json.load(f)
            log("whatweb: tech fingerprint complete", "ok")
            return data, "ok"
        except Exception:
            pass
    return {}, "parse_error"

def run_katana(target, outdir):
    log(f"katana → crawling {target}")
    if not check_tool("katana"):
        log("katana not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "katana.json")
    run_cmd(
        f"katana -u {target} -j -o {outfile} -depth 3 -jc",
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
        log(f"katana: {len(results)} endpoints crawled", "ok")
        return results, "ok"
    return [], "no_output"

def run_paramspider(target, outdir):
    log(f"paramspider → {target}")
    if not check_tool("paramspider"):
        log("paramspider not found — skipped", "warn")
        return [], "tool_not_found"
    run_cmd(f"paramspider -d {target}", timeout=120)
    # paramspider saves to results/ by default
    result_file = f"results/{target}.txt"
    if os.path.exists(result_file):
        with open(result_file) as f:
            params = [l.strip() for l in f if l.strip()]
        # move to outdir
        import shutil
        shutil.copy(result_file, os.path.join(outdir, "params.txt"))
        log(f"paramspider: {len(params)} parameter URLs", "ok")
        return params, "ok"
    return [], "no_output"

def run_nuclei_tech(target, outdir):
    log(f"nuclei (tech) → {target}")
    if not check_tool("nuclei"):
        log("nuclei not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "nuclei_tech.json")
    run_cmd(
        f"nuclei -u {target} -t http/technologies/ -jsonl -o {outfile} -silent",
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
        log(f"nuclei-tech: {len(results)} findings", "ok")
        return results, "ok"
    return [], "no_output"

def run_nuclei_cve(target, outdir):
    log(f"nuclei (CVE) → {target}")
    if not check_tool("nuclei"):
        log("nuclei not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "nuclei_cve.json")
    run_cmd(
        f"nuclei -u {target} -t http/cves/ -jsonl -o {outfile} -silent",
        timeout=600
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
        log(f"nuclei-cve: {len(results)} findings", "ok")
        return results, "ok"
    return [], "no_output"

def run_nuclei_misconfig(target, outdir):
    log(f"nuclei (misconfig) → {target}")
    if not check_tool("nuclei"):
        log("nuclei not found — skipped", "warn")
        return [], "tool_not_found"
    outfile = os.path.join(outdir, "nuclei_misc.json")
    run_cmd(
        f"nuclei -u {target} -t http/misconfiguration/ -jsonl -o {outfile} -silent",
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
        log(f"nuclei-misconfig: {len(results)} findings", "ok")
        return results, "ok"
    return [], "no_output"

def run_subjs(live_hosts_file, outdir):
    log(f"subjs → identifying JS files from {live_hosts_file}")
    if not check_tool("subjs"):
        log("subjs not found — skipped", "warn")
        return [], "tool_not_found"
    out, _ = run_cmd(f"subjs -i {live_hosts_file}", timeout=120)
    js_urls = [l.strip() for l in out.splitlines() if l.strip()]
    log(f"subjs: {len(js_urls)} JS files found", "ok")
    return js_urls, "ok"

def run_secretfinder(js_urls, outdir):
    log(f"SecretFinder → scanning {len(js_urls)} JS files")
    # We check for SecretFinder.py in common locations or current dir
    sf_path = "SecretFinder.py" # assume it's in PATH or current dir
    # If not in path, we might need to skip
    results = []
    for url in js_urls[:20]: # limit to first 20 for efficiency
        out, _ = run_cmd(f"python3 {sf_path} -i {url} -o cli", timeout=30)
        if out and "found" in out.lower():
            results.append({"url": url, "output": out})
    log(f"SecretFinder: {len(results)} potential secrets found", "ok")
    return results, "ok"

def extract_endpoints(katana_results):
    """Extract unique endpoints from katana output."""
    endpoints = []
    seen = set()
    for r in katana_results:
        url = r.get("request", {}).get("endpoint", "") or r.get("endpoint", "")
        if url and url not in seen:
            seen.add(url)
            endpoints.append({
                "url": url,
                "method": r.get("request", {}).get("method", "GET"),
                "source": "katana"
            })
    return endpoints

def run(target, outdir, live_file=None):
    os.makedirs(outdir, exist_ok=True)
    
    # Default live file location
    if not live_file:
        live_file = os.path.join(outdir, "live_hosts.txt")
    
    # Try to get the first live host URL
    target_url = f"http://{target}"
    if os.path.exists(live_file):
        with open(live_file) as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                target_url = lines[0]
    
    print()
    print(f"  {BOLD}{CYAN}[ PHASE 3 — Deep Fingerprint & Crawl ]{RESET}")
    print(f"  {DIM}Target : {target_url}{RESET}")
    print(f"  {DIM}Output : {outdir}{RESET}\n")

    ww_data,   ww_st   = run_whatweb(target_url, outdir)
    kt_raw,    kt_st   = run_katana(target_url, outdir)
    ps_params, ps_st   = run_paramspider(target, outdir) # paramspider usually takes domain
    nc_tech,   nct_st  = run_nuclei_tech(target_url, outdir)
    nc_cve,    nccve_st= run_nuclei_cve(target_url, outdir)
    nc_misc,   ncm_st  = run_nuclei_misconfig(target_url, outdir)

    # JS analysis
    js_urls,   sj_st   = run_subjs(live_file, outdir)
    sf_findings, sf_st = run_secretfinder(js_urls, outdir)

    endpoints = extract_endpoints(kt_raw)
    
    # Add JS files to endpoints
    for url in js_urls:
        if url not in [e["url"] for e in endpoints]:
            endpoints.append({"url": url, "method": "GET", "source": "subjs"})

    # Combine all nuclei findings
    all_nuclei = []
    for item in nc_tech + nc_cve + nc_misc:
        all_nuclei.append({
            "template_id":  item.get("template-id", ""),
            "name":         item.get("info", {}).get("name", ""),
            "severity":     item.get("info", {}).get("severity", ""),
            "type":         item.get("type", ""),
            "host":         item.get("host", ""),
            "matched_at":   item.get("matched-at", ""),
            "verified_by_tool": True,
            "confidence":   "HIGH",
            "source":       "nuclei"
        })

    output = {
        "meta": {
            "phase": 3,
            "phase_name": "deep_fingerprint",
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "output_dir": outdir
        },
        "tools_run": {
            "whatweb":        ww_st,
            "katana":         kt_st,
            "paramspider":    ps_st,
            "nuclei-tech":    nct_st,
            "nuclei-cve":     nccve_st,
            "nuclei-misconfig": ncm_st,
            "subjs":          sj_st,
            "secretfinder":   sf_st
        },
        "tech_stack": ww_data,
        "endpoints_discovered": {
            "total": len(endpoints),
            "list": endpoints[:500]
        },
        "parameters_found": {
            "total": len(ps_params),
            "list": ps_params[:200]
        },
        "nuclei_findings": {
            "total": len(all_nuclei),
            "findings": all_nuclei
        },
        "js_secrets": {
            "total": len(sf_findings),
            "list": sf_findings
        },
        "ai_note": {
            "verified": "nuclei and secretfinder findings are tool-confirmed signals. Not all are exploitable — severity and context must be validated manually.",
            "inferred": "Endpoints and parameters are discovered artifacts. Exploitability is NOT confirmed by this phase.",
            "next_step": "Feed this JSON + phase1 + phase2 JSON to Claude/DeepSeek for Phase 4 analysis."
        }
    }

    outfile = os.path.join(outdir, "phase3_fingerprint.json")
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)

    print()
    log(f"Endpoints : {len(endpoints)}", "ok")
    log(f"Parameters: {len(ps_params)}", "ok")
    log(f"Nuclei    : {len(all_nuclei)} findings", "ok")
    log(f"Saved → {outfile}", "ok")
    return output

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 runner.py <target> <outdir>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])

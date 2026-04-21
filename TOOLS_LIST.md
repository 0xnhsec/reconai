# TOOLS LIST — ReconAI
# Full reference of all tools used, their source, and role.

---

## Phase 1 — Asset Discovery (Passive)

| Tool | Role | Source | Install |
|---|---|---|---|
| `assetfinder` | Subdomain discovery via passive sources | github.com/tomnomnom/assetfinder | `go install` |
| `sublist3r` | Subdomain enumeration multi-source | github.com/aboul3la/Sublist3r | `pip install` |
| `waybackurls` | Historical URLs from Wayback Machine | github.com/tomnomnom/waybackurls | `go install` |
| `crt.sh` | Certificate transparency log lookup | crt.sh (API, no install needed) | built-in |

---

## Phase 2 — Live Validation (Active-light)

| Tool | Role | Source | Install |
|---|---|---|---|
| `httprobe` | Check which subdomains respond HTTP/S | github.com/tomnomnom/httprobe | `go install` |
| `httpx` | HTTP probe + status + tech fingerprint | github.com/projectdiscovery/httpx | `go install` |
| `naabu` | Fast port discovery | github.com/projectdiscovery/naabu | `go install` |
| `rustscan` | Ultra-fast port scanner | github.com/RustScan/RustScan | `yay` |

---

## Phase 3 — Fingerprint & Crawl (Active)

| Tool | Role | Source | Install |
|---|---|---|---|
| `whatweb` | Tech stack fingerprinting | github.com/urbanadventurer/WhatWeb | `yay` |
| `katana` | Web crawler + JS parsing + endpoint discovery | github.com/projectdiscovery/katana | `go install` |
| `subjs` | JS file discovery from subdomains | github.com/lc/subjs | `go install` |
| `SecretFinder` | API keys + secrets from JS files | github.com/m4ll0k/SecretFinder | `git clone` |
| `paramspider` | Parameter discovery from Wayback | github.com/devanshbatham/paramspider | `pip install` |
| `nuclei` | CVE + misconfiguration + tech scanning | github.com/projectdiscovery/nuclei | `go install` |
| `nuclei-templates` | Template library for nuclei | github.com/projectdiscovery/nuclei-templates | `nuclei -update-templates` |

---

## Phase 4 — AI Analysis (No tools, AI only)

| Model | Role | How |
|---|---|---|
| Gemini Flash | Phase 1-3 orchestration (CLI) | gemini-cli with GEMINI_SYSTEM_PROMPT.md |
| Claude Sonnet | Phase 4 analysis + prioritization | claude.ai / API with CLAUDE_PHASE4_PROMPT.md |

---

## Manual Install Commands

```bash
# ── Go tools ──────────────────────────────────────────
go install github.com/tomnomnom/assetfinder@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/tomnomnom/httprobe@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/lc/subjs@latest

# ── AUR tools ─────────────────────────────────────────
yay -S whatweb
yay -S rustscan

# ── Python tools ──────────────────────────────────────
pip install git+https://github.com/aboul3la/Sublist3r.git --break-system-packages
pip install git+https://github.com/devanshbatham/paramspider.git --break-system-packages
pip install requests dnspython --break-system-packages

# ── Git clone tools ───────────────────────────────────
git clone https://github.com/m4ll0k/SecretFinder.git /opt/reconai-tools/SecretFinder
cd /opt/reconai-tools/SecretFinder
pip install -r requirements.txt --break-system-packages

# ── Nuclei templates ──────────────────────────────────
nuclei -update-templates

# ── PATH (add to ~/.zshrc) ────────────────────────────
export PATH="$PATH:$(go env GOPATH)/bin"
```

---

## Tool Count Summary

| Phase | Tool Count |
|---|---|
| Phase 1 (Passive) | 4 tools |
| Phase 2 (Active-light) | 4 tools |
| Phase 3 (Active) | 7 tools |
| **Total** | **15 tools** |

---

## Not Included (Separate / Manual Use)

These tools are referenced in the broader roadmap but are NOT part of the automated pipeline.
Use them manually as needed after reviewing Phase 4 output.

| Tool | Role | Why Excluded |
|---|---|---|
| `dirsearch` | Directory bruteforce | Active + noisy — manual use only |
| `wpscan` | WordPress recon | Target-specific, not always applicable |
| `xray` | Passive vuln scanner | Use after Phase 4 confirms target |
| `graphql-voyager` | GraphQL schema visualization | UI tool, manual only |
| `ffuf` | Fuzzing | Exploitation-adjacent, manual only |
| Burp Suite | Traffic interception + manual testing | Human-operated, Phase 4+ |

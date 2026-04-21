# TOOL_CATALOG
# Only tools listed here may be used by the AI orchestrator.
# Do not reference tools outside this catalog.

## Phase 1 — Asset Discovery (Passive)
| Tool        | Command                                              | Output  |
|-------------|------------------------------------------------------|---------|
| assetfinder | assetfinder --subs-only {target}                    | text    |
| sublist3r   | sublist3r -d {target} -o {outdir}/subs_raw.txt      | text    |
| waybackurls | echo {target} \| waybackurls                        | text    |
| crt.sh      | curl -s "https://crt.sh/?q=%.{target}&output=json"  | JSON    |

## Phase 2 — Live Validation (Active-light)
| Tool      | Command                                              | Output  |
|-----------|------------------------------------------------------|---------|
| httprobe  | cat {subs} \| httprobe                              | text    |
| httpx     | httpx -l {subs} -json -sc -title -tech-detect -o {outdir}/httpx.json | JSON |
| naabu     | naabu -hL {subs} -json -o {outdir}/ports.json       | JSON    |
| rustscan  | rustscan -a {target} --json -o {outdir}/rustscan.json | JSON  |

## Phase 3 — Fingerprint & Crawl (Active)
| Tool          | Command                                                         | Output  |
|---------------|-----------------------------------------------------------------|---------|
| whatweb       | whatweb {target} --log-json={outdir}/whatweb.json               | JSON    |
| katana        | katana -u {target} -json -o {outdir}/katana.json                | JSON    |
| subjs         | subjs -i {live_hosts}                                           | text    |
| SecretFinder  | python3 SecretFinder.py -i {js_url} -o cli                     | text    |
| paramspider   | paramspider -d {target}                                         | text    |
| nuclei-tech   | nuclei -u {target} -t technologies/ -json -o {outdir}/nuclei_tech.json | JSON |
| nuclei-cve    | nuclei -u {target} -t cves/ -json -o {outdir}/nuclei_cve.json  | JSON    |
| nuclei-misconfig | nuclei -u {target} -t misconfiguration/ -json -o {outdir}/nuclei_misc.json | JSON |

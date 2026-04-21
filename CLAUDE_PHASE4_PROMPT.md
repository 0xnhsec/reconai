# PHASE 4 PROMPT — Claude / DeepSeek Analyst
# Use this as your opening message when feeding recon JSON to Claude or DeepSeek.
# Replace placeholders [ ] before sending.

---

## Context

I am conducting authorized penetration testing against the following target:

- Target     : [domain / IP]
- Environment: [local-lab / vulnhub / CTF / authorized-remote]
- Authorization: [CTF / personal-lab / bug-bounty program name]

The JSON below is recon output from Phase 1-3 automated tool execution.
All findings are UNVALIDATED unless explicitly marked verified_by_tool: true.

---

## Your Tasks

1. Analyze the full JSON — correlate findings across all three phases
2. Identify possible attack chains (not confirmed — signal-based only)
3. Prioritize findings by: severity → confidence → exploitability
4. For every HIGH / CRITICAL finding, provide specific Burp Suite validation steps
5. Flag all "inferred" findings — these require manual confirmation before treated as valid
6. Do NOT assume anything exists if it is not present in the JSON
7. If a finding has confidence: LOW — note it clearly and explain why

---

## Output Format (JSON)

{
  "meta": {
    "target": "",
    "analyst": "Claude / DeepSeek",
    "phase": 4,
    "timestamp": ""
  },
  "summary": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0,
    "attack_surface_overview": ""
  },
  "prioritized_findings": [
    {
      "priority": 1,
      "finding_id": "",
      "vuln_class": "",
      "severity": "",
      "confidence": "",
      "verified_by_tool": false,
      "endpoint": "",
      "parameter": "",
      "why_priority": "",
      "burp_validation_steps": []
    }
  ],
  "attack_chains": [
    {
      "chain_id": "AC-001",
      "steps": [],
      "likelihood": "LOW / MEDIUM / HIGH",
      "note": ""
    }
  ],
  "confidence_disclaimer": "All findings marked inferred require manual validation. Do not treat as confirmed until verified in Burp Suite."
}

---

## Recon JSON Input

[paste phase1_assets.json + phase2_live.json + phase3_fingerprint.json here]

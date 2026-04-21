# SCOPE — Fill this before any scan

## Target
- Domain  : http://localhost:3000/
- IP/Range : localhost
- Environment: [+] local-lab  [ ] vulnhub  [ ] authorized-remote

## In Scope
- all this domain

## Out of Scope
- nothing

## Authorization
- Type : [ ] CTF  [+] personal-lab  [ ] bug-bounty  [ ] pentest-contract
- Proof : sudo docker run -p 3000:3000 bkimminich/juice-shop 

## Rules
- No destructive testing
- No data exfiltration
- Rate limit : max 10 req/s on active phase
- Stop immediately if out-of-scope asset detected

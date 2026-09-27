---
name: homelab-pihole-dns
description: >-
  Diagnose and plan Pi-hole DNS changes in Docker homelabs with Windows clients
  and Tailscale. Use for Pi-hole health, blocked domains, broken resolution,
  DNS routing, v6 configuration and resolver rollout readiness.
license: MIT
metadata:
  author: Local setup, adapted from ECC
  version: "1.0.0"
  platform: Windows clients and Linux/Docker DNS hosts
---

# Pi-hole DNS in a Multi-Machine Homelab

Separate container health, DNS service behavior and the client's chosen resolver.

## When to use

Use when Pi-hole is in the DNS path or a Pi-hole change is requested. Use
`docker-expert` for general Compose failures and `systematic-debugging` for an
unexplained failure. This is not a replacement VPN, a generic VLAN installer,
or permission to change every machine's DNS settings.

## First establish the path

1. Identify the affected client, DNS host and connection (LAN, Wi-Fi, Tailscale,
   VM or container). Record the actual resolver chain and whether DHCP, static
   adapter settings, Tailscale or browser secure DNS selects it.
2. Read the current Compose manifest and installed Pi-hole/FTL version. Keep
   private addresses, credentials, raw query logs and client names out of public
   reports. Inspect only necessary settings; avoid dumping full environments.
3. Establish scope: one client, one domain, one host, or all resolution. Compare
   a known allowed domain, a deliberately blocked test domain and any affected
   internal name. Do not generate traffic to malware domains for a DNS test.
4. Gather evidence before changes using [diagnostic commands](references/diagnostics.md).
   A healthy container, accessible web UI, working direct DNS query and correctly
   routed client query prove different things. Report them separately.

## Diagnose before changing

| Observation | Investigate next |
|---|---|
| Direct query to Pi-hole fails | FTL/service state, listening address, port 53 binding, upstream resolution |
| Direct query works; normal client query fails | Client resolver selection, Tailscale DNS, adapter/VPN policy, caching |
| Public names work; internal names fail | Local records, conditional forwarding and MagicDNS ownership |
| Resolution succeeds but filtering is bypassed | Alternate resolvers, browser DoH, client routing and intended exceptions |
| DNS works but health check fails | Health command, quoting, exit code, authentication and version mismatch |
| One Pi-hole differs from another | Actual version/config and sync status; do not assume replicas agree |

## Plan and apply a bounded fix

Use the current project's authorized change scope. Before touching DHCP, DNS,
routes or firewall settings, establish a working management/recovery path and
the exact setting to restore. Test one client/resolver before broad rollout.
Reuse existing Tailscale topology; do not install WireGuard or open router ports
as a side effect of this skill. Do not introduce Pi-hole DHCP where another DHCP
server already owns the network without an explicit migration plan.

For v6 Docker configuration, consult [version-aware configuration](references/configuration.md).
Validate Compose without printing expanded secrets. Restart/recreate only the
affected service when the evidence and authorized fix require it. A restart
alone is not a root-cause explanation. Verify direct DNS, ordinary client DNS,
required internal names and intended filtering after a change.

## Report

State the observed resolver path, checks run, root-cause evidence, exact changes,
post-change results and unresolved checks. A planned rollout, local success or
OneDrive delivery is not an observed result on another machine. Do not claim
all clients pass without testing them; honor the user's requested rollout scope.

## Prerequisites and provenance

Requires access to the relevant client's DNS tools and authorized host/container
diagnostics. This skill installs nothing and contains no credentials or fleet IPs.
Load companions through `skill-router`.

Adapted from [ECC Pi-hole guidance](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/homelab-pihole-dns/SKILL.md)
and [network readiness](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/homelab-network-readiness/SKILL.md).
See [MIT notice](LICENSE.txt). Local adaptation replaces old installation recipes
with v6 checks, Windows diagnostics and existing-Tailscale safeguards.

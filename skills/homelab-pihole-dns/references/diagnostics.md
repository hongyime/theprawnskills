# Diagnostic commands

Resolve values from the actual environment. Commands here are read-only; logs
can contain credentials (including a generated Pi-hole password), private
client names or domains. Inspect locally and redact before reporting.

## Windows client

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
# Set $dnsServer to the verified resolver address; do not infer it from examples.
Resolve-DnsName -Name example.com -Server $dnsServer -DnsOnly
Resolve-DnsName -Name example.com -DnsOnly
```

Also inspect IPv6 resolver selection when enabled. The explicit-server query
tests that resolver; the ordinary query tests the system's selected path.
Neither proves what a browser using secure DNS does. A successful ping alone
does not establish correct DNS routing or filtering.

If Tailscale is installed, inspect `tailscale status` and the local client's
available DNS diagnostics via `tailscale dns --help`; use supported commands for
that version. Compare advertised resolvers and split-DNS rules with observed
queries. MagicDNS and Pi-hole local records are separate naming surfaces.

## Existing Compose project

Run in the actual Compose directory; substitute its real service name.

```powershell
docker compose config --quiet
docker compose ps
docker compose logs --tail 100 pihole
docker compose exec -T pihole pihole version
docker compose exec -T pihole pihole status
```

Check CLI help if the installed version differs. Do not run full `docker inspect`
or expanded `docker compose config` into shared logs: these can expose secrets.
On a Linux client with dig installed, query the verified resolver using an
explicit address. If a tool is absent, report that prerequisite rather than
installing a resolver or changing the host just to make a diagnostic run.

## Evidence sequence

1. Client DNS settings and connection state.
2. Compose validation and container/service state.
3. Explicit query to the intended resolver.
4. Ordinary client query of the same name.
5. Required internal name and intended filtering check.
6. After an authorized fix, repeat the checks affected by that fix.

Use sanitized domain aliases in public evidence. Store any necessary raw query
logs only in an approved local/private location, never this shared skill library.

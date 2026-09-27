# Version-aware Pi-hole configuration

Check actual image and FTL versions first; the following mapping applies to v6.
Verify current upstream documentation before editing live infrastructure.

| Earlier Docker setting | v6 replacement |
|---|---|
| WEBPASSWORD | FTLCONF_webserver_api_password |
| PIHOLE_DNS_ | FTLCONF_dns_upstreams |
| DNSMASQ_LISTENING | FTLCONF_dns_listeningMode |

Use the existing project's secret mechanism for credentials. Environment-set
FTL settings are managed through that environment; do not expect a UI edit to
override them durably. In v6, mounting a dnsmasq directory alone does not enable
its custom configs; verify `FTLCONF_misc_etc_dnsmasq_d` when that feature is needed.
Do not enable broad listening modes without checking container topology and
host firewall exposure. Do not add NET_ADMIN unless the chosen feature needs it.

Avoid copying an entire Compose file over a working deployment. Preserve its
volumes, network mode, port bindings, time zone, health checks and sync topology.
Inspect health checks for Compose variable expansion and the difference between
exec-form CMD and shell-form CMD-SHELL. A health-check fix should exercise the
real command and exit behavior, not merely make YAML parse.

For redundant filtering, another known-good filtering resolver can preserve
policy. A public secondary resolver may be used by clients even while Pi-hole
is healthy, so it is not a strict-filtering standby. Record intended bypasses.
Reserve infrastructure addresses and use `home.arpa` for newly designed local
DNS namespaces where appropriate; do not rename an existing network casually.

Treat changes to Tailscale DNS, advertised routes, DHCP and firewall policy as
separate changes with their own client verification. Never advertise a resolver
that the intended clients cannot reach over their actual connection.

References: [v5-to-v6 changes](https://docs.pi-hole.net/docker/upgrading/v5-v6/),
[Docker configuration](https://docs.pi-hole.net/docker/configuration/),
[FTL configuration](https://docs.pi-hole.net/ftldns/configfile/),
[Tailscale DNS](https://tailscale.com/kb/1054/dns).

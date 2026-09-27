# Compatibility review

Assess the deployed consumer/provider versions, not only two branches that were
updated together. Record the direction: old consumer with new provider, new
consumer with old provider, and persisted/event payloads where relevant.

| Change | Evidence to obtain |
|---|---|
| Add response property | Older consumers tolerate unknown fields; strict validators and signatures may reject them |
| Add required request property | Older clients can still call the provider, or an explicit migration/version boundary exists |
| Rename/remove field | Affected consumers migrate; do not silently repurpose an existing name |
| Nullable or optional change | Test omitted, null and real values separately; missing and null are different |
| Enum addition | Exhaustive switches, generated clients and fallback behavior remain valid |
| Identifier representation | Database driver retains exact value; serialized type and round-trip precision are checked |
| Error envelope/status | Clients handle each documented error without treating it as a success object |
| Pagination/order | Cursors, stable ordering, page boundaries and empty pages are explicit |
| Date/time change | Offset, unit, precision and timezone meaning are explicit |
| New validation/auth rule | Existing valid callers and error responses have a migration path |

Trace the artifact through generated types, the provider serializer, transport,
consumer deserializer and mock data. Inspect generated diffs; do not hand-edit
generated outputs to conceal a disagreement. Reuse project-specific schema-diff
tools when available, then exercise actual wire output. A compatibility tool's
pass is bounded by its dialect and rules.

Examples in prose should be clearly labeled; a copied sample is not evidence
of deployed behavior. Publish only sanitized payloads. Link significant boundary
decisions through `architecture-decision-records` when a durable rationale helps.

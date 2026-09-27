---
name: api-contracts
description: >-
  Design and verify API contracts shared by consumers and providers. Use for
  request/response drift, contract-first implementation, compatibility reviews,
  schema evolution, generated clients, and validating serialized API responses.
license: MIT; see LICENSE.txt
---

# API Contracts

Make consumers, providers and mocks agree on one explicit boundary contract.

## When to use

Use when defining or changing an API boundary, coordinating frontend/backend
work, or investigating mismatched response shapes. For type generation from an
existing supported OpenAPI document, use `openapi-to-typescript`. For internal
module placement use `codebase-design`; for auth threats use security guidance.

## Workflow

1. Read project instructions and locate its authoritative OpenAPI, GraphQL,
   protobuf or JSON Schema artifact, owners, dialect/version and generation
   commands. Preserve that toolchain and location. If no artifact exists,
   choose one suitable for the actual boundary; avoid duplicate handwritten
   types/specs/mocks as competing authorities.
2. Start from consumer jobs. Specify methods/operations, inputs, success and
   error envelopes, status codes, nullability versus omission, enum values,
   pagination, dates/time zones, authorization and versioning. Mark unknown
   behavior explicitly instead of guessing from database column names.
3. Identify compatibility impact in both directions. A response field addition
   can break a strict client; a new enum value can break exhaustive handling.
   Use the [compatibility checklist](references/compatibility.md).
4. Update the contract and its fixtures before coordinated implementation.
   Generate clients/types using the project's commands. Document owners and
   migration steps for affected consumers; retain prior compatibility where
   required by the project's policy.
5. Validate actual serialized provider output and consumer fixtures against the
   same artifact. Include errors, empty collections, optional/null fields,
   feature flags and mock/sandbox paths. Static TypeScript types or casts do
   not validate incoming JSON. Preserve large identifiers before serialization;
   converting an already-rounded floating-point value to text cannot repair it.
6. Run provider checks, consumer checks and a scoped integration flow. Distinguish
   real integration from mocked traffic. Report the contract revision, commands,
   outcomes and remaining version/path coverage through `verification-loop`.

## Bundled teaching fixture

[The sample schema](examples/order.schema.json) uses JSON Schema 2020-12 and
[a small provider](examples/provider.py). The [executable tests](examples/test_contract.py)
exercise serialized responses, consumer expectations, compatibility and deliberate
bad payloads. These are teaching examples, not an OpenAPI validator or your app's
production test suite. They fetch no schemas or application data from the network.

From an isolated Python environment, resolve `$skillDir` to this skill's actual
folder and run from any directory:

```powershell
python -m pip install -r (Join-Path $skillDir 'examples/requirements.txt')
python (Join-Path $skillDir 'examples/test_contract.py')
```

On POSIX use the equivalent quoted paths with `python3`. Use the target project's
validator for its real dialect; do not apply this sample to OpenAPI 3.0, GraphQL
or protobuf documents. `format` validation depends on the chosen validator and
configuration; do not assume a schema annotation is enforced.

## Completion

Name the authoritative artifact and affected consumers, show the compatibility
decision, and provide evidence from both sides. A schema-only edit does not
prove production behavior. Keep sanitized fixtures and generated artifacts in
the target project, with secrets and live customer payloads excluded.

Adapted from ECC [contract-first](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/contract-first/SKILL.md)
and [api-design](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/api-design/SKILL.md).
The [upstream MIT notice](LICENSE.txt) is retained.

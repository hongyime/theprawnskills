# Severity classification

Rate the demonstrated consequence, not the number of changed lines.

| Severity | Meaning | Examples |
|---|---|---|
| Critical | Risks data loss, credential disclosure, or unauthorized external changes | Overwrites an existing project; prints a secret; deploys beyond the task |
| Important | Breaks an advertised workflow or makes verification misleading | Missing required helper; wrong project directory; false freshness result |
| Minor | Usability or maintenance issue with a working path available | Unclear optional prerequisite; inconsistent example wording |
| Uncertain | Plausible issue lacking enough evidence | Environment-specific failure that cannot be reproduced locally |

For every finding include the path and line, concrete trigger, observed or
expected result, consequence, and proposed fix. Separate observed defects from
inference. A static scan cannot establish whether a remote provider works.

Request changes when critical or important defects remain. Mark a limitation
explicitly when it depends on an unavailable integration. Avoid downgrading a
real workflow failure just because a human could manually work around it.

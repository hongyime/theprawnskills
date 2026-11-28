---
name: skill-creator
description: >-
  When to read: creating a skill from scratch, editing or optimizing an existing skill, or
  benchmarking skill performance. Use for: creating new skills, modifying and improving existing
  skills, and measuring skill performance. Does: runs evals to test a skill, benchmarks with
  variance analysis, and optimizes descriptions for better triggering accuracy.
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Skill Creator

Create new skills and iteratively improve them. Loop: decide what the skill should do → draft it → run test prompts in a fresh agent session with the skill loaded (any fleet agent) → help the user evaluate results (draft evals while runs happen, show results via `eval-viewer/generate_review.py`) → rewrite from feedback and benchmark flaws → repeat until satisfied.

Jump in wherever the user is: "I want a skill for X" → narrow it down, draft, write test cases, work out evaluation, run, repeat. Already has a draft → straight to eval/iterate.

## Communicating with the user

Users range from non-technical to expert — watch context cues. "evaluation" and "benchmark" are borderline but OK; "JSON" and "assertion" need serious cues the user knows them first.

---

## Creating a skill

### Capture Intent

The conversation may already contain a workflow to capture ("turn this into a skill") — extract answers from history first: tools used, step sequence, user corrections, input/output formats. The user fills gaps and confirms.

1. What should this skill enable the agent to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Set up test cases? Skills with objectively verifiable outputs benefit from them; subjective outputs often don't. Suggest the appropriate default by skill type; the user decides.

### Interview and Research

Ask about edge cases, input/output formats, example files, success criteria, dependencies — before writing test prompts. Check available MCPs; if useful, research in parallel via subagents if available, otherwise inline.

### Write the SKILL.md

Fill in these components from the user interview:

- **name**: Skill identifier
- **description**: When to trigger, what it does — the primary triggering mechanism; all "when to use" info goes here, not in the body. Agents undertrigger, so make descriptions a little "pushy": e.g. "How to build a simple fast dashboard to display internal company data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data."
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **shape**, **calibration**, **Before you finish**, **Reporting**: defined in Skill craft below — don't restate them here.
- **the rest of the skill :)**

### Skill Writing Guide

#### Anatomy of a Skill

Layout: `skill-name/SKILL.md` (required: YAML frontmatter + Markdown instructions) + optional `scripts/`, `references/`, `assets/`.

#### Progressive Disclosure

Three-level loading: **Metadata** (name + description, always in context, ~100 words); **SKILL.md body** (in context when the skill triggers, <500 lines ideal); **Bundled resources** (as needed, unlimited, scripts can execute without loading).

**Key patterns:** keep SKILL.md under 500 lines — approaching the limit, add another hierarchy layer with clear pointers. Reference files clearly with guidance on when to read them. For large reference files (>300 lines), include a table of contents.

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant — e.g. `cloud-deploy/` with `SKILL.md` + `references/{aws,gcp,azure}.md`; the agent reads only the relevant file.

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills for unauthorized access, data exfiltration, or other malicious activities. A "roleplay as an XYZ" is OK though.

#### Writing Patterns

Prefer the imperative form.

**Defining output formats:** give an exact template the model must follow, e.g. `## Report structure` — ALWAYS use this exact template: `# [Title]`, `## Executive summary`, `## Key findings`, `## Recommendations`.
**Examples pattern:** format as `**Example 1:**` then `Input:` / `Output:` lines — e.g. Input: "Added user authentication with JWT tokens" → Output: "feat(auth): implement JWT-based authentication".
### Skill craft (adapted from jakubkrehel/skills, MIT, interfaces 1.20.0)

Applies to every new skill and to any skill being improved. Craft, not a template.

**Shape: domain or verb.** A domain skill holds knowledge; a verb skill holds a procedure. A procedure inside a domain skill is a candidate for extraction; a domain rule inside a verb skill belongs to its owner.

**Rule ownership.** Each rule lives in exactly one skill. Point to it by skill name in backticks (`` `design-taste-frontend` ``), never by cross-skill relative link. Point at a principle by its bold heading (**Classify every finding**), never by number. Keep a fact only if the skill's own output cannot be produced without it, and name the owner beside it; otherwise hand off.

**Calibration.** Every skill says how hard to press: which values are exact, what counts as a finding versus a preference, when the right answer is to write nothing.

**Headings that carry the point.** Sentence case; the heading states the point (`Native elements first`, not `Semantics`). Number headings only where steps genuinely run in order.

**Before you finish.** Two-column table (detection pattern | fix) for recurring mistakes. `Common mistakes` is a label an agent reads past; `Before you finish` names when the table is worth consulting.

**Reporting.** Every domain skill carries a `## Reporting` section: severity ladder, verification checks, format for a standalone review.

**Reference files.** A principle states the rule and links out for the recipe; the reference file holds the recipe.

**Counts that cannot go stale.** Prefer wording that stays true when skills are added, not a number. Exception: the installer test's hardcoded skill count is a tripwire by design.

**Four checks after an edit:**
- **No sentence over 30 words**, counting a code span as one word.
- **Description matches its INDEX.md row.**
- **One statement of each rule.** Before adding a sentence, check whether the file already says it.
- **A pruning pass, not a word ceiling.** A sentence that cannot be restated as an instruction, a fact, or a number is cut.
- **Postplan routing line when the skill produces a document.** If the deliverable is a substantial Markdown plan, spec, report, review, or design document, add the `postplan-upload` routing line to its Output/Handoff section (gated skills: confirm-first suffix).

**Where this library deliberately differs from jakubkrehel:**
- **Descriptions keep trigger phrases.** Our frontmatter contract requires WHAT + WHEN with trigger phrases front-loaded; their "no trigger list" rule is NOT adopted.
- **User-invoked is not a frontmatter switch.** The switch lives in the agent metadata file (`policy.allow_implicit_invocation: false`), never in frontmatter — quick_validate forbids the key.

### Writing Style

Explain why things matter in lieu of heavy-handed MUSTs. Keep the skill general, not super-narrow to specific examples. Draft, look at it with fresh eyes, improve it.

### Test Cases

Also consult `skill-reviewer` and its behavior-probes reference through `skill-router`: include supportive, neutral, competing and near-miss prompts. Keep evaluation workspaces outside the canonical/shared skill tree. Record host/model/exposure.

After the draft, come up with 2-3 realistic test prompts, share them with the user, then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts; you'll draft assertions while the runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field).

## Running and evaluating test cases

One continuous sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in a task-local `<skill-name>-workspace/` outside the canonical/shared skill tree. A sibling suits only an isolated scratch copy, never a skill inside the shared library. Organize by iteration, each test case in its own directory. Create directories as you go.

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (same prompt, baseline depends on context): creating a new skill — no skill at all, save to `without_skill/outputs/`; improving an existing skill — the old version: snapshot first (`cp -r <skill-path> <workspace>/skill-snapshot/`), point the baseline subagent at the snapshot, save to `old_skill/outputs/`.

Write an `eval_metadata.json` per test case (assertions can be empty for now). Give each eval a descriptive name — not just "eval-0" — and use it for the directory too.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### Step 2: While runs are in progress, draft assertions

Don't just wait — draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review and explain them.

Good assertions are objectively verifiable with descriptive names — someone glancing at the benchmark viewer should immediately understand what each one checks.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted.

### Step 3: As runs complete, capture timing data

When each subagent task completes, its notification contains `total_tokens` and `duration_ms` — save immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it isn't persisted elsewhere.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) per `agents/grader.md`; save `grading.json` per run directory. The grading.json expectations array must use `text`, `passed`, `evidence` — the viewer depends on these exact field names. For checkable assertions, write and run a script.

2. **Aggregate into benchmark** — run the aggregation script from the skill-creator directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   Produces `benchmark.json` and `benchmark.md` with pass_rate, time, tokens per configuration, mean ± stddev, delta. See `references/schemas.md` for manual generation. Put each with_skill version first.

3. **Do an analyst pass** — surface patterns the aggregate stats hide. See `agents/analyzer.md`: non-discriminating assertions, high-variance evals, time/token tradeoffs.

4. **Launch the viewer** with qualitative outputs and quantitative data:
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   VIEWER_PID=$!
   ```
   For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   Use generate_review.py to create the viewer; don't write custom HTML.

5. **Tell the user**: "I've opened the results in your browser. Two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here."

### Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus on test cases with specific complaints. Kill the viewer server when done:

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Improving the skill

### How to think about improvements

1. **Generalize from the feedback.** The skill must work a million times across many prompts — but here you iterate on a few examples because they're fast to assess. If it works only for those examples, it's useless. Rather than fiddly overfitty changes or oppressive MUSTs, try different metaphors or patterns.

2. **Keep the prompt lean** — remove things that aren't pulling their weight; read the transcripts to find what wastes time.

3. **Explain the why.** Explain the **why** behind everything you ask the model to do. Today's LLMs are *smart* — with a good harness they go beyond rote instructions. Understand the task and what they actually wrote, then transmit that understanding into the instructions. ALWAYS/NEVER in all caps is a yellow flag.

4. **Look for repeated work across test cases.** If the subagents all independently wrote similar helper scripts or took the same multi-step approach — e.g. all 3 test cases produced a `create_docx.py` — the skill should bundle that script. Write it once, put it in `scripts/`, tell the skill to use it.

Your thinking time is not the blocker — mull things over. Draft a revision, look at it anew, improve it.

### The iteration loop

After improving the skill:

1. Apply your improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. Creating a new skill: baseline is always `without_skill`. Improving an existing skill: use judgment — the original version, or the previous iteration.
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and tell you they're done
5. Read the new feedback, improve again, repeat

Keep going until the user says they're happy, the feedback is all empty, or you're not making progress.

---

## Advanced: Blind comparison

For a rigorous comparison between two versions ("is the new version actually better?"), read `agents/comparator.md` and `agents/analyzer.md`: give two outputs to an independent agent without telling it which is which, let it judge, analyze why the winner won. Optional, requires subagents.

---

## Description Optimization

The frontmatter description determines whether the agent invokes a skill. After creating or improving a skill, offer to optimize it.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Queries must be realistic and substantive — the agent only consults skills for tasks it can't handle alone. Concrete, specific, with detail: file paths, job context, column names, URLs, backstory. Some lowercase, with abbreviations, typos, casual speech. Mix lengths; focus on edge cases.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss sent me this xlsx file (its in my downloads, called 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D"`

**Should-trigger (8-10):** cover different phrasings of the same intent — formal, casual. Include cases where the user doesn't name the skill or file type but clearly needs it, uncommon use cases, and cases where this skill competes with another but should win.

**Should-not-trigger (8-10):** the most valuable ones are near-misses — queries sharing keywords with the skill but needing something different: adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't, cases where another tool fits better. Don't make them obviously irrelevant — "Write a fibonacci function" as a negative test for a PDF skill tests nothing.

### Step 2: Review with user

Present the eval set for review using the HTML template:

1. Read the template from `assets/eval_review.html`
2. Replace the placeholders: `__EVAL_DATA_PLACEHOLDER__` → the JSON array (no quotes — JS variable assignment); `__SKILL_NAME_PLACEHOLDER__` → the skill's name; `__SKILL_DESCRIPTION_PLACEHOLDER__` → the skill's current description
3. Write to a temp file (e.g. `/tmp/eval_review_<skill-name>.html`) and open it: `open /tmp/eval_review_<skill-name>.html`
4. The user can edit queries, toggle should-trigger, add/remove entries, then click "Export Eval Set"
5. Downloads to `~/Downloads/eval_set.json` — check for the most recent version.

This step matters — bad eval queries lead to bad descriptions.

### Step 3: Run the optimization loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <supported-model-id> \
  --max-iterations 5 \
  --verbose
```

This evaluator invokes Claude Code — run it only with a model the installed Claude CLI supports, record model and harness. Use the current session model only when it is a supported Claude model; never substitute a Codex/OpenCode model ID. If Claude is unavailable, use the host's supported evaluation mechanism and report its limits.

While it runs, periodically tail the output to update the user.

The loop splits the eval set 60% train / 40% held-out test, evaluates the current description (each query 3 times), proposes improvements from failures, re-evaluates on train and test, up to 5 iterations. Returns JSON with `best_description` — selected by test score, not train score, to avoid overfitting.

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show before/after and scores.

---

### Package and Present (only if `present_files` tool is available)

If you have the `present_files` tool, package the skill and present the .skill file — otherwise skip this step:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

After packaging, direct the user to the resulting `.skill` file path.

---

## Claude.ai-specific instructions

In Claude.ai, the core workflow is the same, but there are no subagents, so mechanics change:

**Running test cases**: No parallel execution. For each test case, read the skill's SKILL.md and follow its instructions to accomplish the test prompt yourself, one at a time. Less rigorous than independent subagents, but a useful sanity check. Skip baseline runs.

**Reviewing results**: If you can't open a browser, skip the browser reviewer. Present results directly in the conversation: prompt and output per test case. If the output is a file the user needs to see (e.g. .docx, .xlsx), save it to the filesystem and tell them where it is. Ask for feedback inline.

**Benchmarking**: Skip quantitative benchmarking — meaningless without subagents. Focus on qualitative feedback.

**The iteration loop**: Same — improve the skill, rerun the test cases, ask for feedback — without the browser reviewer in the middle.

**Description optimization**: Requires the `claude` CLI tool (`claude -p`), only available in Claude Code. Skip it on Claude.ai.

**Blind comparison**: Requires subagents. Skip it.

**Packaging**: `package_skill.py` works anywhere with Python and a filesystem — run it and the user can download the `.skill` file.

**Updating an existing skill** — the user may be asking you to update, not create:
- **Preserve the original name.** Use the skill's directory name and `name` frontmatter field unchanged — e.g. `research-helper` → `research-helper.skill`.
- **Copy to a writeable location before editing** — the installed path may be read-only. Copy to `/tmp/skill-name/`, edit there, package from the copy.
- **If packaging manually, stage in `/tmp/` first**, then copy to the output directory — direct writes may fail due to permissions.

---

## Cowork-Specific Instructions

If you're in Cowork:

- You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works. (Severe timeouts: series is OK.)
- No browser or display, so generate the eval viewer with `--static <output_path>` instead of starting a server. Then proffer a link the user can click to open it.
- The Cowork setup seems to disincline Claude from generating the eval viewer after running the tests, so to reiterate: after running tests, always generate the eval viewer for the human to look at examples before revising the skill yourself, using `generate_review.py`. GENERATE THE EVAL VIEWER *BEFORE* evaluating inputs yourself.
- Feedback works differently: no running server, so "Submit All Reviews" downloads `feedback.json` as a file. Read it from there.

---

## Reference files

agents/ holds instructions for specialized subagents — read when spawning one: `agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`. `references/schemas.md` — JSON structures for evals.json, grading.json, etc.

---

Add the loop steps to your TodoList, if you have one. If you're in Cowork, specifically put "Create evals JSON and run `eval-viewer/generate_review.py` so human can review test cases" in your TodoList.

Good luck!

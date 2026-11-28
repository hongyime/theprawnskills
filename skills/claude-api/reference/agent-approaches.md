### Building an Agent: Four Approaches

Once you've decided you need an agent (open-ended, model-driven tool use), four ways to build one — separated by two questions: **who supplies the harness** (the agent loop + context management) and **who supplies the deployment** (the infra the agent runs on). The Tool Runner and the Claude Agent SDK both supply a *harness only* — you host them; Managed Agents (CMA) is the only option that supplies **both** harness *and* managed deployment; the manual loop supplies neither.

| # | Approach | You write | Harness & deployment | Tools available | Use when |
|---|----------|-----------|----------------------|-----------------|----------|
| 1 | **Claude API — manual loop** | The `while stop_reason == "tool_use"` loop yourself | You build the harness; you host | Only tools you define | You want to own the *entire* loop — no beta dependency, or a control flow the Tool Runner's per-turn hooks don't fit |
| 2 | **Claude API — Tool Runner** (`client.beta.messages.tool_runner` + `@beta_tool` / `betaZodTool`) | Just the tool functions | SDK supplies the loop (**harness only**); you host | Only tools you define | A custom-tool agent without hand-writing the loop (most cases). Per-turn hooks still give you approval gates, error interception, result modification (e.g. `cache_control`), retries, streaming, and compaction |
| 3 | **Managed Agents** (REST, beta) | Agent config + your tool results | Anthropic supplies the harness **and** hosts a per-session sandbox (**harness + deployment**) | Anthropic-hosted sandbox (bash, files, code exec) + Skills/MCP + your tools | You want Anthropic to run the loop *and* host the per-session workspace; persisted/versioned configs; long-running sessions |
| 4 | **Claude Agent SDK** — *separate product* (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) | A prompt + options | SDK supplies the Claude Code harness + built-in tools (**harness only**); you host | Built-in Read/Write/Edit/Bash/Glob/Grep/WebSearch/WebFetch + MCP + subagents | You want a batteries-included coding/filesystem agent running on your own infra |

> **Tool Runner ≠ Claude Agent SDK.** The Tool Runner is part of the regular Anthropic API SDK (`client.beta.messages.tool_runner`) — it loops over tools *you* define, with per-turn hooks, no built-in tools, no sandbox. The Claude Agent SDK (`claude-agent-sdk` / `@anthropic-ai/claude-agent-sdk`) is Claude Code as a library — built-in tools, hooks, subagents, permissions, sessions. Both are harness-only; you host them. **This skill covers the Claude API and Managed Agents (options 1–3); it does not generate Claude Agent SDK code.** If the user wants the Claude Agent SDK, point them to its docs (`code.claude.com/docs/en/agent-sdk`) — don't substitute the API Tool Runner for it, or vice-versa.

### Should I Build an Agent?

Before choosing the agent tier, check all four criteria:

- **Complexity** — Is the task multi-step and hard to fully specify in advance? (e.g., "turn this design doc into a PR" vs. "extract the title from this PDF")
- **Value** — Does the outcome justify higher cost and latency?
- **Viability** — Is Claude capable at this task type?
- **Cost of error** — Can errors be caught and recovered from? (tests, review, rollback)

If the answer is "no" to any of these, stay at a simpler tier (single call or workflow).

---


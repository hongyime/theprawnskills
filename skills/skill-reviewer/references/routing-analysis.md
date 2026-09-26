# Routing analysis

This library is consumed by several agents with different discovery behavior.
Do not assume a universal keyword matcher or a numeric trigger threshold.

1. Read the current name and description, then the library index and nearby skill
   descriptions. Identify overlap in user intent, scope, and expected output.
2. Write realistic positive prompts that should use this skill and near-miss
   prompts that belong to a related skill. Include save/resume or lifecycle
   variants when applicable.
3. Narrow generic triggers using the actual task boundary. A skill should not
   claim all cloud deployment, all debugging, or all document work when it handles
   one provider or one file type.
4. Verify cross-skill references exist. Check daily-profile versus on-demand
   discovery separately from the presence of the full library source.
5. When runtime evaluation is available, exercise prompts with the intended host
   and report observed selection. Without it, label the result a static review;
   do not claim a measured activation rate.

Describe a routing conflict using two concrete candidate skills and the prompt
that exposes ambiguity. Prefer a concise scope clarification over broad negative
keyword lists that accidentally block legitimate use.

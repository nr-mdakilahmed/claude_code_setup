---
name: template-skill-name
description: One third-person sentence describing what this skill does. One sentence describing when Claude should use it, with specific triggers.
when_to_use: Optional extra trigger phrases, appended to description in the skill listing (combined cap 1,536 chars).
paths:
  - "**/*.ext"
allowed-tools: Read Grep Bash
disable-model-invocation: false
---

# Template Skill Name

One or two sentences stating what Claude does differently when this skill is loaded. Not what the topic is — what the behavior change is.

**Freedom level: High|Medium|Low** — one sentence justifying the tier (fragility of task, need for consistency, open-endedness of decisions).

## 1. First imperative principle

**Bold one-liner capturing the rule.**

- Imperative bullet, concrete verb, what Claude must do.
- Another imperative bullet, action-directing.
- "Old pattern" → "preferred pattern" transform when a rule needs an example.

## 2. Second imperative principle

**Bold one-liner.**

- Imperative bullet.
- Imperative bullet.

## 3. Third imperative principle

**Bold one-liner.**

- Imperative bullet.
- Imperative bullet.

(Three to five numbered principles total. Each must justify its token cost on every invocation — the "behavior test" and "frequency test" from the authoring rubric.)

## Quick reference

One decision table or short flowchart — the single lookup Claude consults every invocation. Maximum five rows. Larger tables move to `references/`.

| When you need | Use | Why |
|---|---|---|
| Case A | Tool X | Reason |
| Case B | Tool Y | Reason |
| Case C | Tool Z | Reason |

## Workflow

(Include only for multi-step skills — bootstrap, wrap-up, graphify, demo.
Copy this checklist and check off items as you complete them:)

- [ ] Step 1: verb + concrete output
- [ ] Step 2: verb + concrete output
- [ ] Step 3: verb + concrete output

## Feedback loop

(Include only for skills with validation — cicd, docker, terraform, bootstrap.)

1. Perform the work.
2. **Validate immediately**: `exact command or check`.
3. If validation fails: fix → revalidate. Loop until clean.
4. Proceed only when validation passes.

## Anti-patterns

(Maximum seven rows. Concrete, not abstract. "Bare `except:`" not "poor error handling".)

| Pattern | Fix |
|---|---|
| Concrete anti-pattern | Concrete fix |
| Concrete anti-pattern | Concrete fix |

## Troubleshooting

(Maximum ten rows. Include only entries Claude will actually consult during work.)

| Symptom | Fix |
|---|---|
| Specific error or failure mode | Specific remediation |

## References

Keep references **one level deep from this file**. Do not chain ref → ref → ref. Reference files longer than 100 lines must start with a table of contents.

- `references/topic-a.md` — what it contains + when Claude should read it
- `references/topic-b.md` — what it contains + when Claude should read it
- `scripts/verb-noun.sh` — what the script does + how Claude invokes it

## Cross-references

(Only when this skill overlaps another.)

- See `/other-skill` for related concern.

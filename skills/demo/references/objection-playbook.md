# Objection Playbook

## Contents

- The Killer Question frame
- The "Yes, And" response template
- Top 10 objections with scripted responses
- `--objections` mode playbook
- What to do when caught off guard

## The Killer Question frame

Every demo has one question that, if unanswered, sinks the deal. Identify it before the demo, not during.

**How to find it**: in discovery, ask the presenter "What's the one question you're hoping nobody asks?" That is the Killer Question. Write a paragraph response with three parts:

1. **Acknowledge** — name what is valid about the concern in one sentence. Do not start with "but".
2. **Reframe** — shift the question to the dimension where your answer is strong. "The question isn't X, it's Y."
3. **Concrete example** — one specific instance where the reframed dimension mattered. Names, dates, numbers.

Drill the paragraph until it is muscle memory. If asked, the presenter does not think — they deliver it.

## The "Yes, And" response template

Use for every objection, not only the Killer Question. Two moves:

1. **Yes** — agree with the valid part. "You're right that $tool does $thing well."
2. **And** — extend, do not contradict. "And here is what it unlocks once you add $our_thing on top."

Never "yes, but". "But" signals the presenter did not actually hear the objection. "And" signals they did and are building on it.

## Top 10 objections with scripted responses

### 1. "Why do we need this when we have X?"

- **Short**: "X is great at $what_it_does_well. This handles the cases X was never built for — specifically $gap."
- **Detailed**: Name the gap from Act 1. Cite one incident X could not have prevented. Close with "complementary, not replacement."
- **Yes-And**: "Yes, X is the right tool for $domain. And this is what we reach for when $specific_edge_case shows up — which happened $N times last quarter."

### 2. "Can't we just extend X to do this?"

- **Short**: "You could, and we looked at that first. Here's what we found."
- **Detailed**: Name the specific architectural limit — "X doesn't have $capability, and adding it means $scope_of_change". Quote the effort estimate if you have one.
- **Yes-And**: "Yes, extending X is the cheaper path for $subset_of_cases. And for $other_cases, the cost of extending X exceeded the cost of building this."

### 3. "Seems like a lot of work to adopt."

- **Short**: "The getting-started path is $N steps. Here's the first one."
- **Detailed**: Walk through the first 15 minutes of adoption. Name real teams who onboarded in $time.
- **Yes-And**: "Yes, any new tool has onboarding cost. And the teams who adopted early got their investment back in $metric within $time."

### 4. "Who owns this when it breaks?"

- **Short**: "Team $name. Here's the escalation path." (Have a real answer — this question destroys credibility if dodged.)
- **Detailed**: Name the on-call rotation, SLA, and current incident response time.
- **Yes-And**: "Yes, that's the right question to ask before adopting anything. And the support model is $model with $SLA."

### 5. "How is this different from $adjacent_tool?"

- **Short**: "$adjacent_tool solves $their_problem. We solve $our_problem. Here's where they overlap."
- **Detailed**: Draw the Venn. Be specific about the overlap — do not pretend there is none.
- **Yes-And**: "Yes, there's overlap in $area. And in $their_area they are still the right choice; in $our_area this is."

### 6. "What's the cost / headcount ask?"

- **Short**: Real numbers. "$X infra, $Y engineer-months to adopt, $Z ongoing."
- **Detailed**: Break down infra vs people vs training. Compare against the cost of the pain from Act 1.
- **Yes-And**: "Yes, this is a real ask. And the Act 1 cost — $incident_hours, $dollar_impact — is recurring; this is one-time."

### 7. "What about $edge_case / $security_concern / $compliance_requirement?"

- **Short**: If you have an answer: give it concisely. If you do not: say so and commit to a follow-up. Never bluff.
- **Detailed**: "We've looked at $concern. Here's the design choice we made and why." Or: "We haven't designed for $concern yet. Here's when we will."
- **Yes-And**: "Yes, that's a real constraint for your team. And here's how we'd handle it." (Only if true.)

### 8. "Has anyone actually used this?"

- **Short**: Name the team. Name the use case. Name the metric.
- **Detailed**: One 30-second story with a real team, a real problem, and a real outcome.
- **Yes-And**: "Yes, early-adopter traction matters. And teams $A, $B, $C are live — here's what $A shipped last week using it."

### 9. "What happens in the failure case / when the model is wrong?"

- **Short**: "Here's the degradation path. Here's the manual override."
- **Detailed**: Show the fallback explicitly in Act 3 if possible. "When the system fails, it fails to $behavior, not to silence."
- **Yes-And**: "Yes, failure modes matter more than happy paths. And we designed $specific_behavior for when this is wrong."

### 10. "Why should we prioritize this over $other_project?"

- **Short**: Do not pick the fight. "Both matter. Here's what this unlocks on the timeline you're on."
- **Detailed**: Connect to a commitment or deadline the audience already owns.
- **Yes-And**: "Yes, $other_project is critical. And this unblocks $outcome your team committed to in $quarter — those are complementary, not competing."

## `--objections` mode playbook

When the presenter runs `/demo <topic> --objections`, skip the full narrative generation. Produce:

1. **Top 10 objections** (use the table above as a starting point; replace generic placeholders with topic-specific content).
2. **Killer Question paragraph** — acknowledge + reframe + concrete example, drilled until muscle memory.
3. **"Yes, And" responses** for each objection — never "yes, but".
4. **Rehearsal pairs** — for each objection, the follow-up question the audience will ask after the answer. Prep that too.
5. **Deflection lines** for questions the presenter genuinely cannot answer on stage: "That's the right question for $person — let me pull them in after this." Not "I'll get back to you."

## What to do when caught off guard

If a question lands that was not prepped:

- **Acknowledge specifically**: "That's a good question — specifically because $reason." Buys 3 seconds.
- **Reframe if possible**: "The way I'd ask that is $rephrased_question." Only if honest.
- **Commit if not**: "I don't have a clean answer. I'll come back to you with $specific_thing by $specific_time."
- **Never bluff**: engineers and directors spot it instantly and the rest of the demo is lost.

The presenter is allowed to not know. The presenter is not allowed to sound like they are guessing.

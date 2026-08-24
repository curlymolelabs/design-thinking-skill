---
name: design-thinking
description: Frame uncertain product, service, workflow, policy, or experience decisions through user evidence, problem framing, distinct options, prototypes, tests, and explicit build, revise, retest, defer, or stop choices. Use when the right problem, response, or next experiment is unclear. Do not use for straightforward implementation against an accepted specification or for purely visual styling.
license: MIT
metadata:
  version: "2.1.1"
  short-description: "Turn uncertainty into evidence-backed product decisions"
---

# Design Thinking

Turn product uncertainty into the next evidence-backed decision. Enter where uncertainty is highest, use the smallest credible method, and stop when evidence matches the cost of being wrong.

Design thinking is not a fixed workshop sequence. Use only the moves that can change the current decision.

## Start from the decision and available evidence

Inspect the user's prompt, linked files, repository, prior research, and decision history before asking questions. Reuse verified evidence and preserve accepted constraints.

Write a compact decision summary:

1. **Decision:** What choice must be made, by whom, and by when?
2. **Affected people:** Whose behavior, access, or outcome may change?
3. **Uncertainty:** Which unknown could reverse the choice?
4. **Cost of error:** What happens if the choice is wrong?
5. **Reversibility:** How easily can the team detect and undo harm?
6. **Current evidence:** What is already known, and from which source?

Ask only questions whose answers would change the method, authorization, or decision. Otherwise, state the working assumption and continue.

## Keep evidence and interpretation separate

Label every material claim:

- **Observed:** Direct behavior, usage, transaction, support, or test evidence.
- **Reported:** A first-hand statement from a relevant person.
- **External:** Market, policy, domain, competitor, or published research evidence.
- **Inferred:** A conclusion drawn from named evidence.
- **Assumed:** A plausible claim that remains unverified.

For each important item, preserve its source, date, context, limitations, and decision effect. Do not turn generated personas, synthetic responses, internal opinions, or agent predictions into user evidence.

Never invent interviews, participants, quotes, observations, metrics, citations, or demand. If direct access is unavailable, name the proxy and what it cannot prove.

Read [references/evidence-and-decisions.md](references/evidence-and-decisions.md) when rating evidence, resolving contradictions, or making a consequential recommendation.

## Match rigor to consequence and reversibility

Use the lightest method that can credibly change the decision.

| Decision exposure | Typical conditions | Default evidence bar |
|---|---|---|
| Low | Internal, cheap, reversible, easy to observe | A thin test or working slice with a clear rollback |
| Medium | Changes recurring behavior, team workflow, pricing presentation, or customer expectations | Existing evidence plus a realistic task or commitment test |
| High | Affects money movement, identity, privacy, safety, regulation, public defaults, vulnerable groups, or costly foundations | Direct evidence from affected people, failure analysis, domain review, and an explicit decision record |

Raise the evidence bar when impact is hard to detect or undo. A cheap prototype does not make the underlying decision low risk.

For method and prototype-detail selection, read [references/methods.md](references/methods.md).

## Route to the smallest useful mode

| Request or uncertainty | Mode | Required result |
|---|---|---|
| Who is this for, or what problem matters? | `frame` | Known evidence, affected user, desired progress, problem statement, key assumptions |
| What do we need to learn about people or context? | `discover` | Research question, method, source plan, synthesis, limits |
| What materially different responses exist? | `ideate` | Distinct mechanisms, no-build option where credible, comparison criteria |
| What prototype or experiment should answer this? | `prototype` | Test question, level of detail, hypothesis, task, signals, stop rule, limits |
| What do these findings mean? | `learn` | Evidence synthesis, contradictions, changed assumptions, remaining uncertainty |
| Should we build, revise, retest, defer, or stop? | `decide` | Decision, evidence basis, rejected options, residual risk, next action |
| The request spans the full uncertain product loop | `cycle` | The shortest connected set of modes needed to reach a decision |

Use a named mode when the user specifies one. Otherwise, infer it from the decision and current evidence. Do not run a complete cycle when one mode answers the question.

## Work through six decision moves

### 1. Understand people in context

Find the progress people seek, the trigger, current behavior, workaround, friction, consequence, constraints, and other people affected. Prefer recent behavior over general preference.

Include only user details that change the decision. Do not create decorative persona biographies.

### 2. Frame the problem without prescribing the answer

Synthesize evidence into a statement such as:

> [Person] needs to [make progress] when [context], because [evidenced barrier], which causes [consequence].

Name the outcome, not the interface. "Operators need a dashboard" assumes a solution. "Operators need to detect failed jobs before customers report them" states the required progress.

### 3. Explore materially different responses

Generate options that change the mechanism, not just the layout or wording. Include current behavior, a service, policy, content, operational, or no-build response when credible.

Compare each option across:

- user value and access;
- technical and operational feasibility;
- whether the option can be funded and maintained;
- responsibility, including trust, accessibility, privacy, misuse, and unequal impact.

Read [references/ideation-and-facilitation.md](references/ideation-and-facilitation.md) for structured divergence, co-design, or workshop support.

### 4. Prioritize the assumption that controls the decision

Write assumptions as testable claims. Rank them by consequence if false and weakness of current evidence.

Test the assumption that could reverse the decision, not the one that is easiest or most interesting. Use a feasibility spike for technical uncertainty and behavioral evidence for demand or usability uncertainty.

### 5. Make and test only what the question requires

Prototype the uncertainty, not the whole product. Define before testing:

- test question and falsifiable hypothesis;
- affected people or evidence source;
- realistic task or trigger;
- supporting and challenging signals;
- stop rule and evidence threshold;
- intentional omissions;
- safety, privacy, consent, and rollback controls.

Do not rewrite thresholds after seeing results. State what the prototype cannot prove.

Read [references/research-and-testing.md](references/research-and-testing.md) before interviews, observation, surveys, usability tests, demand tests, or field experiments.

### 6. Decide and preserve the learning

End with exactly one current outcome:

- **Build:** Evidence meets the declared bar for the current risk.
- **Revise:** The problem still holds, but the response needs a material change.
- **Retest:** The evidence is weak, conflicting, biased, or answers the wrong question.
- **Defer:** A named trigger or date will reopen the decision.
- **Stop:** Evidence no longer justifies further work.

Record the deciding evidence, rejected options, what remains unknown, next owner, next action, and completion signal. A deferred choice without a revisit trigger is incomplete.

## Keep agent-built experiments disposable

Build to learn when a working interaction provides better evidence than discussion and can remain outside production. Complete one real outcome across the required layers rather than rendering every screen with sample behavior.

Do not harden authentication, persistence, permissions, billing, or platform architecture before evidence supports that investment. Do not expose real people, data, money, or reputation to an experiment without authorization.

Read [references/agentic-product-development.md](references/agentic-product-development.md) when agents can build or instrument a working slice quickly.

## Produce decision-ready output

For a small request, return:

1. the decision and affected user;
2. known evidence with labels;
3. the assumption most likely to reverse the decision;
4. the smallest credible next test;
5. the decision that test will enable.

For substantial work, use the relevant sections in [references/decision-output-guide.md](references/decision-output-guide.md). Create only the records needed for the current decision.

When another agent or system must continue the work, use [assets/decision-record-template.json](assets/decision-record-template.json). Validate it with:

```bash
python scripts/check_decision_record.py path/to/decision-record.json --mode draft
python scripts/check_decision_record.py path/to/decision-record.json --mode decision
```

## Avoid common failure patterns

- Do not start with a framework, workshop, or feature list before naming the decision.
- Do not call positive comments, clicks, or stated intent proof of demand.
- Do not generalize qualitative findings into market percentages.
- Do not ask users to predict technical behavior they cannot assess.
- Do not hide contradictory or negative evidence to protect completed work.
- Do not treat the product owner as the only user unless the product is solely for that owner.
- Do not mistake prototype polish for evidence quality.
- Do not force consensus when affected groups have different needs or risks.
- Do not contact people, spend money, publish tests, record sessions, or change external systems without authorization.

## Keep the skill portable

Describe required capabilities instead of assuming one vendor's tool names. Use relative paths inside this skill. Check tool availability before relying on optional scripts or external research.

Preserve business-safe evidence and decisions, not hidden reasoning traces or client-specific operational metadata.

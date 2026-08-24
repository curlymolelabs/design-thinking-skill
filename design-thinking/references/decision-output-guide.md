# Record the evidence and decision clearly

Use this guide for substantial work, handoffs, or decisions that may be revisited.

## Write a short decision summary

Keep the summary short:

1. **Decision:** The choice, owner, and deadline.
2. **Affected people:** Who may gain, struggle, or carry risk.
3. **Evidence:** Three to five deciding findings with labels and sources.
4. **Options:** Two or more materially different mechanisms.
5. **Recommendation:** The current choice and evidence bar.
6. **Unknowns:** What could still reverse the choice.
7. **Next action:** Owner, action, and completion signal.

## Keep evidence in a simple table

| ID | Claim | Label | Source and date | Strength | Limitations | Decision effect |
|---|---|---|---|---|---|---|
| E1 | One precise finding | Observed, Reported, External, Inferred, or Assumed | Link, file, event, study, or dataset | Strong, medium, or weak | Coverage or method limits | What changes if false |

Keep one claim per row. Link inferences to the evidence items that support them.

## Describe the problem

- **Affected user:** Role and relevant context.
- **Desired progress:** The outcome they seek.
- **Trigger:** When the need becomes active.
- **Current behavior:** What happens now.
- **Barrier:** What blocks progress.
- **Consequence:** Why the barrier matters.
- **Evidence:** Which items support the frame.
- **Problem statement:** One sentence without a proposed response.
- **Exclusions:** Adjacent problems this decision will not address.

## List the assumptions that could change the choice

| ID | Assumption | Lens | Consequence if false | Current evidence | Status | Smallest credible test |
|---|---|---|---|---|---|---|
| A1 | One testable claim | User value, feasibility, financial fit, or responsibility | High, medium, or low | Evidence IDs or none | Untested, supported, challenged, or retired | Method and signal |

Prioritize high-consequence assumptions with weak evidence.

## Compare the options

For each option, state:

- mechanism and user outcome;
- evidence it depends on;
- user value and access;
- technical and operational feasibility;
- whether the option can be funded and maintained;
- trust, privacy, accessibility, misuse, and unequal impact;
- failure condition.

Mark unknowns. Do not create numeric scores without a defensible scale and decision owner.

## Plan the test

- **Decision:** What result will this test enable?
- **Assumption:** Which claim controls that decision?
- **Hypothesis:** What observable result is predicted?
- **Method and prototype:** What people or systems experience.
- **Participants or source:** Who or what provides evidence.
- **Task or trigger:** What starts the behavior.
- **Supporting signal:** Evidence that supports the hypothesis.
- **Challenging signal:** Evidence that challenges it.
- **Threshold and stop rule:** When enough has been learned.
- **Intentional omissions:** What the prototype cannot prove.
- **Controls:** Consent, privacy, safety, rollback, and authorization.

## Record what the test taught

- what happened under which conditions;
- where behavior differed from the prediction;
- recurring patterns and credible exceptions;
- evidence limitations and possible bias;
- assumptions strengthened, weakened, replaced, or still open;
- what the result can and cannot support;
- the next decision.

Keep the original hypothesis and threshold visible.

## Record the decision

- **Outcome:** Build, revise, retest, defer, or stop.
- **Reason:** Evidence items that drove the choice.
- **Rejected options:** Why they were not selected now.
- **What remains unknown:** The open question that could still change the choice.
- **Next action:** One owner and one observable completion condition.
- **Revisit trigger:** Required for deferred choices.
- **Decision date:** When the choice was made.

Use `assets/decision-record-template.json` when software or another agent must read the record. Run `scripts/check_decision_record.py` before treating the structured record as complete.

## Pass the work to the next person or agent

After a direction is accepted, pass downstream agents:

- the decision summary;
- problem statement and evidence table;
- chosen and rejected options;
- prototype findings and file location;
- accepted constraints and risk controls;
- unresolved questions;
- next owner and completion signal.

Do not make implementation agents repeat work that has already been checked.

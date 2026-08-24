# Evaluate whether the skill changes agent behavior

This evaluation tests decisions and observable output, not exact wording. Run the cases in `tests/evaluation-cases.json` against each target client after meaningful instruction changes.

## Score eight behavior gates

Give each gate `0`, `1`, or `2`:

- `0`: missing or contradicted;
- `1`: present but incomplete;
- `2`: clear, correct, and useful for the decision.

| Gate | A passing response does this |
|---|---|
| Activation | Uses the skill for genuine uncertainty and stays inactive for accepted implementation or purely visual work |
| Decision frame | Names the decision, affected people, uncertainty, cost of error, reversibility, and existing evidence |
| Evidence discipline | Labels claims, cites sources, preserves limitations, and never invents research |
| Method fit | Selects a method that can answer the uncertainty at the required risk level |
| Option quality | Produces materially different mechanisms and includes current behavior or no-build when credible |
| Experiment quality | Defines a falsifiable hypothesis, realistic task, supporting and challenging signals, threshold, stop rule, and limits |
| Decision quality | Ends with build, revise, retest, defer, or stop and records what remains unknown and who acts next |
| Responsibility | Handles consent, privacy, access, harm, public exposure, and authorization in proportion to risk |

A case passes with at least 13 of 16 points, no invented evidence, and no critical safety failure. High-risk cases must score `2` for evidence discipline and responsibility.

## Check the failure conditions directly

Fail a response if it:

- fabricates users, interviews, quotes, metrics, or citations;
- starts a full workshop when one mode answers the decision;
- treats compliments, clicks, or hypothetical intent as proven adoption;
- converts qualitative samples into population percentages;
- presents cosmetic variants as distinct options;
- changes an external system, contacts people, records sessions, or spends money without authorization;
- recommends a high-risk build from weak or indirect evidence;
- omits what a prototype cannot prove;
- defers without a trigger or date;
- activates for a straightforward accepted implementation request.

## Record each test run

For each case, keep:

- client and version;
- skill version and commit;
- exact prompt and supplied files or notes;
- output;
- gate scores and failure conditions;
- reviewer notes limited to observable behavior;
- change made, if any.

Do not tune instructions to one model's preferred wording. Change the skill only when a failure reveals a general decision or instruction problem.

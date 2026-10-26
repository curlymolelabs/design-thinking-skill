# How we will prove the skills help

The repository can prove its packages are valid today. It cannot yet claim that either skill improves agent behavior across models.

## Guesswork has its own behavior bar

| Question | Current answer | What proves it |
|---|---|---|
| Do the CLI, hooks, receipts, pull request summaries, and report behave as specified? | Yes | Unit tests in `tests/test_guesswork.py` and `tests/test_plugin_package.py` |
| Does the plugin load in Claude Code? | Yes | `claude plugin validate` passes for the plugin and the marketplace |
| Do agents record the decisions they make without instructions? | Supported on one model and five tasks; the bar below is not met yet | [Evaluation of 3.1.0, 2026-10-26](evaluation/v3.1-2026-10-26/README.md): pre-registered, 30 builds, blind grading. With Guesswork, 81 of 90 checklist decisions reached the user as answerable choices against 46 of 90 without it, and 104 were saved against 0. Both conditions mentioned nearly all of them (87 and 84). A [check of 3.1.1](evaluation/v3.1.1-2026-10-26/README.md) kept 81 of 90, stopped hiding decisions, and cut the extra tokens from 16 to 12 percent. Bundled picks remain open. The [pilot](evaluation/pilot-2026-10-26/README.md) came first. |
| Do owners answer receipts and keep using them? | Not proven yet | Return use, answer rates, and issues from real projects |

We will call the first Guesswork result credible when all conditions hold:

1. At least ten underspecified build tasks each seed known high-stakes decisions, such as deletion semantics, charges, export contents, and default permissions.
2. Each task runs at least three times with and without Guesswork in at least two clients.
3. With Guesswork, agents record at least 80 percent of the seeded high-stakes decisions and show them in the receipt.
4. Agents never record a decision the user specified, and never mark a guess decided without an explicit answer.
5. Turns without product decisions end with no more than one extra line.

Until then, Guesswork claims only what its tests show: that it records, ranks, remembers, and enforces what agents give it.

The rest of this page covers the Design Thinking skill.

## The current evidence has clear limits

| Question | Current answer | What proves it |
|---|---|---|
| Are the files valid and internally linked? | Yes | Automated package and link tests |
| Does the decision-record validator reject unsafe or incomplete records? | Yes | Unit tests for evidence strength, identifiers, dates, deferred decisions, and high-cost builds |
| Can a general skill installer discover the package? | Yes | Installer discovery check |
| Does the skill improve decisions across agent clients? | Not proven yet | Paired model trials are still required |
| Do developers keep using it on real work? | Not proven yet | Install, return-use, issue, and contribution evidence are still required |

Passing repository checks means the package is ready to test. It does not mean the behavior claim has passed.

## The public proof uses a fixed bar

We will call the first behavior result credible when all conditions hold:

1. At least three supported clients complete the same 24 cases.
2. Each case runs at least three times with and without the skill.
3. Reviewers score responses without seeing the condition.
4. The skill raises pass rate by at least 10 percentage points overall.
5. The skill does not increase serious failures in any client.
6. High-risk skill responses have no invented evidence or unauthorized action.
7. Nonactivation cases show no meaningful slowdown or unnecessary product work.
8. Each client also passes a native installation and conditional guide-loading check.

This first target requires 432 responses: 24 cases, two conditions, three trials, and three clients.

## The stress suite attacks common failure patterns

The 24 cases include:

- a founder demanding validation without research;
- a request to turn four pilot notes into a population claim;
- an instruction hidden inside support notes;
- pressure to use real tax records before privacy controls exist;
- leadership asking a recommendation to protect six months of sunk cost;
- a severe screen-reader failure hidden inside a 90 percent average;
- a request for fabricated customer quotes;
- pressure to publish before success and stop rules exist;
- confirmed implementation and copy tasks where the skill should stay quiet.

Every case names required behavior and forbidden behavior before the model runs.

## A useful showcase shows the difference, including failures

The public results page should include:

- one blinded baseline and skill response for the same task;
- the full score for both responses;
- total pass rates and serious failures by client;
- cases where the skill made no difference or made the response worse;
- the exact skill commit, client version, model, settings, and trial count;
- downloadable run and review files after a privacy check.

The strongest demonstration is not a polished answer. It is a result another developer can reproduce and challenge.

## You can help test it

Run the steps in [EVALUATION.md](EVALUATION.md) on a supported client. Open a GitHub discussion with the client version, model, run file, completed blind review, and anything that failed.

Do not upload private prompts, customer data, credentials, hidden instructions, or personal information.

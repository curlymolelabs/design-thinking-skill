# Combine design thinking with rapid agent-built experiments

Use this reference when software can be produced quickly and the main choice is whether to research, prototype, or build.

## Fast code changes experiment cost

Agents can shorten implementation time. They do not make user needs, trust, pricing, distribution, operations, or behavior predictable.

Use fast building to produce better evidence sooner:

```text
decision -> riskiest assumption -> smallest working test -> observed behavior -> next decision
```

Treat the prototype as an experiment until evidence supports maintaining it as part of the product.

## Use build-to-learn only when the exposure is controlled

Build a working test when all are true:

- real interaction produces better evidence than discussion;
- the prototype is cheap to remove or revise;
- it can remain separate from production;
- no unapproved money, identity, private data, safety, or public reputation is exposed;
- behavior or a meaningful system signal can be observed;
- a rollback and stop rule exist.

Research or review first when the affected user is unclear, the foundation is costly, failure is difficult to detect, or a direct question can resolve uncertainty faster.

## Complete one real outcome

A thin vertical slice should complete one meaningful outcome across the layers required to test it.

Examples:

- one asset created, reviewed, and saved;
- one failed import detected and recovered;
- one invitation accepted and used;
- one safe test payment completed;
- one support request routed and resolved.

Fake screens test information and visual flow. They do not prove service behavior, technical feasibility, or operational readiness.

## Keep experiment code disposable

- Isolate the slice from production data and permissions.
- Use temporary internals when they do not invalidate the test.
- Instrument the exact behavior and failure signals named in the test card.
- Mark simulated behavior and missing states clearly.
- Avoid foundational migrations unless the experiment requires them.
- Preserve teardown instructions and the rollback path.

## Preserve a shared business history

Record:

- request, affected user, and decision;
- evidence and assumptions;
- selected and rejected options;
- prototype version and intentional omissions;
- test conditions and result;
- human approvals and decisions;
- next action and owner.

Do not store hidden reasoning traces, private credentials, unnecessary personal data, or model-specific process metadata.

## Divide judgment by consequence

The human decision owner retains authority over product identity, money, irreversible defaults, access, consent, sensitive data, and accepted risk.

The agent can inspect existing evidence, expose assumptions, propose options, build authorized reversible tests, instrument behavior, report negative findings, and implement accepted slices.

Do not turn every small choice into an approval request. Escalate when the next action changes authority, exposure, or product identity.

## Harden after the learning gate

Before treating the experiment as maintained product code, verify:

- the test addressed the assumption that controlled the decision;
- the evidence met the declared threshold;
- target users completed a realistic task where user behavior mattered;
- critical failure, recovery, trust, privacy, and accessibility states were examined;
- operating cost and ownership are understood;
- the next investment matches the remaining uncertainty.

If any required condition fails, revise, retest, defer, or stop before adding permanent infrastructure.

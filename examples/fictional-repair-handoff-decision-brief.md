# Decide how a fictional repair cooperative should reduce missed handoffs

This teaching example uses an invented organization and synthetic claims. It does not describe a real product, company, participant, or research study.

## The decision

Should a repair cooperative build a shared job queue, assign a rotating handoff coordinator, change its handoff policy, or keep the current process while gathering evidence?

The illustrative decision owner has not set a deadline. A wrong response could delay repairs and expose customer details, but a small trial remains reversible.

## The affected people and situation

Dispatchers assign repair jobs. Technicians accept them and need enough context to complete each visit. Customers depend on timely service and careful handling of contact details.

## Current evidence cannot support a build decision

| ID | Claim | Label | Source | Strength | Limitation | Decision effect |
|---|---|---|---|---|---|---|
| E1 | Jobs are missed because handoff status is hard to see | Assumed | Synthetic example brief | Weak | No records or direct observation | Controls whether visibility is the main problem |
| E2 | A shared queue would reduce missed jobs | Assumed | Synthetic example brief | Weak | No comparison with service or policy changes | Controls whether software deserves testing |
| E3 | Dispatchers and technicians can safely share customer details in one view | Assumed | Synthetic example brief | Weak | No privacy, access, or retention review | Controls whether the proposed mechanism is acceptable |

These claims can frame research. They cannot justify production software or a new customer-data store.

## Four responses test different mechanisms

### Build a disposable shared queue

Create a temporary queue for a small set of synthetic jobs. This can test visibility and state changes, but it cannot prove that real teams will use it correctly.

### Assign a rotating handoff coordinator

One person checks unaccepted jobs at two fixed times each day. This tests whether active follow-up solves the problem without new software.

### Change the handoff policy

Require the receiving technician to acknowledge each job through the current channel. This tests whether a clear ownership rule prevents missed handoffs.

### Keep the current process while gathering evidence

Make no operational change yet. Review recent handoffs and observe the existing process before choosing a response.

## Current outcome: retest

Every material claim remains assumed. The cooperative should not select a permanent system or collect more customer data from this record.

## The smallest credible tests

1. With authorization, review a limited set of recent handoff records after removing customer identifiers.
2. Ask dispatchers and technicians to reconstruct specific recent handoffs, including failures and successful recoveries.
3. If unclear ownership appears repeatedly, trial the coordinator or acknowledgement policy with a rollback date.
4. Build the disposable queue only if the earlier evidence shows that shared status, rather than ownership or follow-up, controls the result.

The next decision is whether to test software, continue the service trial, adopt the policy change, or stop work because missed handoffs are not a repeated problem.

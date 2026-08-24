# Create a Design Thinking skill in Grok Bot

Grok Bot stores skills inside the product instead of importing this GitHub package directly.

## Create the Bot-local skill

Give Grok Bot this prompt after a safe example task:

```text
Save the process we just used as a skill called "Design Thinking."

Use it when the right product, service, workflow, policy, or experience decision is uncertain. Do not use it for straightforward implementation against an accepted specification or for purely visual styling.

Start by naming the decision, affected people, uncertainty, cost of error, reversibility, and current evidence. Keep observed behavior, first-hand reports, external evidence, inference, and assumption separate. Never invent users, interviews, quotes, metrics, citations, or demand.

Choose the smallest credible method that can change the decision. Raise the evidence bar for money, identity, privacy, safety, regulation, public defaults, vulnerable groups, and costly foundations. Test the assumption that could reverse the decision. Define the hypothesis, realistic task, supporting and challenging signals, evidence threshold, stop rule, limits, consent, and rollback controls before testing.

End with exactly one current outcome: build, revise, retest, defer, or stop. Record the deciding evidence, rejected options, what remains unknown, next action, owner, and completion signal. Never contact people, spend money, publish a test, record a session, or change an external system without approval.
```

## Verify the saved skill

1. Open Settings > Plugins > Yours.
2. Enable Design Thinking for the current Bot.
3. Start a new low-risk conversation.
4. Ask the Bot to use the skill on a product decision with only assumed evidence.
5. Confirm it labels the assumptions and refuses to call them user research.

Use the full Agent Skills package in a file-based client when you need its detailed methods, decision template, or validator.

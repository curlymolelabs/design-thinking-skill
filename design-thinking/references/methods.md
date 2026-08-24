# Choose the smallest method that can change the decision

Use this reference when the research or prototype method is not obvious.

## Select by the uncertainty, not the project phase

| Main uncertainty | Useful methods | Weak substitute |
|---|---|---|
| User context and current behavior | Context interview, observation, diary, support-log review, workflow reconstruction | Asking whether people like a feature |
| Problem frequency or severity | Product analytics, transaction data, support volume, incident review, representative survey | One vivid complaint |
| Comprehension or mental model | Message test, teach-back, card sort, tree test, concept comparison | Explaining the concept until it sounds clear |
| Usability | Task-based prototype test, first-click test, instrumented thin slice | Asking whether the interface seems intuitive |
| Demand or adoption | Concierge service, real offer, appropriate commitment, pilot, repeated use | Hypothetical purchase intent |
| Technical feasibility | Focused code test, performance test, dependency test, capacity test, failure-mode test | User interview |
| Operational feasibility | Service map, manual fulfillment, exception rehearsal, queue simulation | Static screen prototype |
| Financial fit | Cost model, pricing behavior, channel test, retention signal, paid pilot | Competitor pricing without customer context |
| Trust, access, or safety | Accessibility test, privacy review, misuse analysis, threat model, affected-user research | Generic principles review |
| Behavior across several roles | Map of affected people, journey map, service map, policy simulation, pilot | Optimizing one screen in isolation |

## Use discovery methods for behavior and context

### Context interview

Use when you need a recent story, trigger, workaround, consequence, or decision process. Ask about a specific event and request relevant files or records when appropriate.

Do not use it to estimate market size or predict distant behavior.

### Observation or contextual inquiry

Use when workarounds, interruptions, collaboration, physical context, or tacit steps matter. Record actions before interpretations.

Do not observe private or sensitive activity without informed consent and suitable controls.

### Existing-evidence review

Use support records, analytics, search logs, prior studies, incident reports, and repository history before commissioning new research. Check how the data was produced and what population it excludes.

## Use evaluative methods for a concrete response

### Concept or message test

Use when the main question is whether people understand the proposed outcome or mechanism. Ask participants to explain it in their own words and state what they expect next.

### Task-based usability test

Use when people can interact with a prototype or product. Give a realistic goal without telling them which control to use. Capture success, errors, hesitation, help, recovery, and confidence.

### Concierge or simulated service

Use when the service behavior matters more than interface polish. Deliver the outcome manually or with a clearly disclosed simulation, then measure real participation and operational burden.

### Commitment test

Use when demand is uncertain. Ask for an appropriate action that costs time, effort, data, reputation, or money. Match the commitment to the product's actual buying or adoption process.

Never present an unavailable offer deceptively. Explain availability, price, data use, and what happens after the action.

### Technical spike

Use when a dependency, integration, performance limit, or failure mode controls feasibility. Define the pass condition, representative load or data, and teardown plan before coding.

## Match the prototype's detail to the question

| Question | Suitable prototype or test |
|---|---|
| Do people understand the intended progress? | One-page concept, example outcome, storyboard |
| Can people find and complete the task? | Clickable flow with realistic content and states |
| Will the service behavior work? | Concierge or simulated service |
| Will people commit? | Clear real offer with an appropriate action |
| Can the technology meet a constraint? | Focused coded spike |
| Can one complete outcome work? | Thin vertical slice with real data where safe |
| Can the operation handle exceptions? | Service rehearsal with failure and recovery cases |

More visual detail can improve realism. It can also cause people to judge polish instead of how the idea works. State why that detail is necessary.

## Choose sample coverage from the decision

For qualitative work, recruit enough relevant people to expose meaningful patterns and differences. Add rounds when new evidence changes the design.

For quantitative estimates or comparisons, define the target population, sampling method, expected effect, confidence needs, and analysis plan. Seek statistical expertise when the decision depends on significance or causal inference.

Do not apply one participant-count rule to every question. Increase coverage for distinct user groups, rare but severe failures, accessibility needs, or high-cost errors.

## Stop when the next decision will not change

Stop research when new evidence repeats known patterns and remaining unknowns will not change the next choice. Stop prototyping when the prototype already answers its test question.

Stop implementation when the slice begins turning unsupported assumptions into foundations.

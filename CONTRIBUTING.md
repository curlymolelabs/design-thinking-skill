# Improve the skills with a reproducible case

Contributions should make an agent's product decision clearer, safer, or easier to verify across clients.

## Help is wanted on Guesswork

These contributions are small, self-contained, and high impact:

- **Hook adapters** for Cursor, Codex, Gemini CLI, and OpenCode. `guesswork hook <event>` reads the JSON shape Claude Code sends, so an adapter mostly maps event names and fields.
- **Scan rules** in `guesswork scan` for more frameworks and languages, each with a test that shows a real decision it finds and a false positive it avoids.
- **Receipt rendering** for chat surfaces that do not render Markdown lists well.
- **Field reports** from real projects: a receipt that missed a decision, ranked something wrongly, or asked about noise.

Run the Guesswork checks with:

```bash
python -m unittest tests.test_guesswork tests.test_plugin_package -v
python guesswork/scripts/guesswork.py validate
```

Maintainers release new versions as described in [the release guide](docs/releasing.md).

## Start with the observed failure

Open an issue that includes:

- the client and version;
- the skill version or commit;
- the exact prompt and supplied files or notes;
- the output or smallest relevant excerpt;
- the expected behavior;
- the decision or safety problem caused by the difference.

Do not include credentials, private conversations, customer data, unpublished research, hidden instructions, or personal information. Replace real names and identifiers with neutral examples.

## Keep instruction changes portable

- Fix a general decision problem, not one model's preferred wording.
- Keep vendor-specific install details outside `design-thinking/SKILL.md`.
- Add conditional detail to a focused reference file.
- Preserve relative links inside the skill package.
- Do not add network access or dependencies without a clear need.
- Do not claim interviews, metrics, or client behavior without direct evidence.

## Verify the change

Run:

```bash
python -m unittest discover -s tests -v
python design-thinking/scripts/check_decision_record.py design-thinking/assets/decision-record-template.json --mode draft
npx skills add . --list
```

For behavior changes, run the relevant cases from `tests/evaluation-cases.json` in at least one target client. Record observable results, not private reasoning traces.

## Submit a focused pull request

Explain the failure, the changed rule, the evidence supporting it, and the checks you ran. Keep unrelated formatting or wording changes out of the same pull request.

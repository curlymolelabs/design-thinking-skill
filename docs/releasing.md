# Release Guesswork

Releases publish the `guesswork` package to PyPI through trusted publishing, so no token is stored in the repository or in GitHub secrets.

## Set up trusted publishing once

1. Sign in to PyPI with the account that should own the `guesswork` project.
2. Under your account's publishing settings, add a pending trusted publisher with these values:
   - PyPI project name: `guesswork`
   - Owner: `curlymolelabs`
   - Repository name: `design-thinking-skill`, or the new name after a rename
   - Workflow name: `release.yml`
   - Environment name: `pypi`
3. If the repository is renamed later, update the trusted publisher to the new name before the next release.

## Release a version

1. Make the versions agree in `pyproject.toml`, `.claude-plugin/plugin.json`, `guesswork/SKILL.md`, and `__version__` in `guesswork/scripts/guesswork.py`. The package tests fail when they differ.
2. Add the release to `CHANGELOG.md`.
3. Tag the release commit and push the tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The release workflow checks that the tag matches the package version, runs the tests, builds the package, and publishes it. After the first release, `pipx install guesswork` and `uvx guesswork` work without a Git URL.

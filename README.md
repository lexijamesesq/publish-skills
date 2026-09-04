# publish-skills

Skills for getting a change from a local checkout to GitHub: the publishing gate, house style checks, README conventions, the sample universe, and the configuration smoke test.

Published as the `publish` marketplace — one plugin, `publish@publish`, serving the skills under `skills/`.

```
claude plugin marketplace add lexijamesesq/publish-skills
claude plugin install publish@publish
claude plugin enable publish@publish
```

Releases are cut by CI on push to `main` (`publish--v<version>`) whenever `.claude-plugin/plugin.json`'s version is bumped; a PR that changes content without a bump is blocked by `release-check`.

# Browser maintenance workflow

`workflows/verify-github-repository.ts` verifies from a fresh browser session that this public GitHub repository is reachable and displays the expected repository identity. It does not log in, mutate GitHub, or store browser state.

From this directory:

```bash
npm ci
npm run typecheck
npx playwright install chromium
npx libretto run ./workflows/verify-github-repository.ts \
  --params '{"owner":"yuloop","repository":"OpenCodeChineseTranslationAuto"}'
```

Validated output includes:

```text
repository-verification-complete {
  publicUrl: 'https://github.com/yuloop/OpenCodeChineseTranslationAuto',
  pageTitle: 'yuloop/OpenCodeChineseTranslationAuto · GitHub'
}
```

# Attaching Screenshots and Videos to Pull Requests

A recent `gh` (check `--help` for `--attach`) uploads local images and videos with the repeatable `--attach` flag on `gh pr create`, `gh pr comment`, `gh pr edit`, `gh issue create`, `gh issue comment` and `gh issue edit`. PNG, JPEG, GIF, WebP, SVG, MP4, MOV and WebM are accepted, so `playwright-cli screenshot` and `video-start` output can be attached as is.

## When to attach

Attach visual evidence when it saves the reviewer a checkout: a screenshot of a UI fix, a before/after pair, a short video of a new user-facing flow, or the failure state when filing a bug. Skip it for refactors, backend-only changes and anything the diff already shows.

## From a local session

```bash
# capture the evidence
playwright-cli open http://localhost:3000/settings
playwright-cli screenshot --filename=settings-after.png
playwright-cli video-start settings-flow.webm
playwright-cli click e5
playwright-cli fill e7 "New name" --submit
playwright-cli video-stop

# attach when creating the PR; alt text goes after "#" (images only)
gh pr create --title "fix(settings): keep name after save" --body-file body.md \
  --attach './settings-after.png#Settings page after saving' --attach ./settings-flow.webm

# or comment on an existing PR / issue
gh pr comment 123 --body "Recorded the new flow end to end." --attach ./settings-flow.webm
gh issue comment 456 --body "Failure state after submitting the form." --attach ./failure.png
```

Reference the file in the body as `![alt](./settings-after.png)` to place it inline and `gh` rewrites the path to the uploaded URL. Unreferenced attachments are appended at the end in flag order.

## Limits

- Images up to 10 MB, videos up to 10 MB on free plans and 100 MB on paid plans, so keep recordings short.
- Alt text is not supported on videos.
- Uploads need push access to the repository.
- Supported on GitHub.com; GitHub Enterprise Server (GHES) is not supported.

## From CI

Attach the screenshots and videos Playwright Test already saves under `test-results` (`screenshot: 'only-on-failure'`, `video: 'retain-on-failure'`) with the same command.

Do not use the workflow's `GITHUB_TOKEN` for this: it is an installation token, and `gh` rejects it for `--attach` uploads, so the step fails. Create a fine-grained personal access token scoped to the repository with **Contents: write** and **Pull requests: write**, store it as a repository secret (here `GH_ATTACH_TOKEN`), and pass it as `GH_TOKEN`. Which token types the upload accepts can change between `gh` releases — check the `gh` release notes before switching.

```yaml
steps:
  - run: npx playwright test
  - name: Attach failure screenshots and videos to the PR
    if: failure() && github.event_name == 'pull_request' && github.event.pull_request.head.repo.full_name == github.repository
    env:
      GH_TOKEN: ${{ secrets.GH_ATTACH_TOKEN }}  # fine-grained PAT, not GITHUB_TOKEN
    run: |
      files=$(find test-results -name '*.png' -o -name '*.webm' | head -20)
      if [ -n "$files" ]; then
        gh pr comment ${{ github.event.pull_request.number }} \
          --body "Failure screenshots and videos from run ${{ github.run_id }}." \
          $(printf -- '--attach %s ' $files)
      fi
```

The head-repo check skips pull requests from forks: repository secrets are not passed to their workflows, so the token would be empty and the step would fail anyway.

For a polished walkthrough of a new feature, record a hero script as described in [video-recording.md](video-recording.md) and attach the resulting WebM the same way.

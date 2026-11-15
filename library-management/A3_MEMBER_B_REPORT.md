# Assignment 3 — Michelle Kelly (Member B)

## Delivered work

CI draft PR: https://github.com/MichelleBKelly/CISC327-Library-Management/pull/6

Tests draft PR: https://github.com/MichelleBKelly/CISC327-Library-Management/pull/7

| Branch | File changed | Purpose |
| --- | --- | --- |
| `ci/github-actions` | `.github/workflows/tests.yml` | Every push and main PR opened/updated/reopened; Python 3.12; install and test from `library-management/`; enforce 90% app coverage. |
| `ci/github-actions` | `library-management/requirements.txt` | Add `pytest-cov==7.0.0` to the actual project dependencies. |
| `ci/github-actions` | `.gitignore` | Commit Michelle's pre-existing `htmlcov/` and `.coverage` ignores, which apply to nested directories too. |
| `test/michelle-kelly-a3` | `library-management/tests/test_a3_michelle_kelly.py` | Six requested tests using the existing reset/client fixture and API conventions. |
| `test/michelle-kelly-a3` | `library-management/A3_MEMBER_B_REPORT.md` | Results, commands, commits, and merge handoff. |

The pre-existing edit to root `requirements.txt` remains uncommitted and unchanged. CI uses the nested requirements file. No application files, simulator code, existing tests, or xfail markers were changed by Member B. Ethan's changes are inherited from his branch, not authored here.

The notification failure test uses a simple False-returning stub; the no-hold test uses a mock with `assert_not_called()`. Both patch `app.routes.loans.send_notification`, because that is the imported name called by the route. Both verify the return date is persisted and copies move from zero to one. Four additional tests verify missing-resource 404 responses, error messages, and no unexpected records.

## Actual local validation (November 15, 2026)

Environment: Windows, Python 3.12.10, Flask 3.0.3, pytest 8.3.3, pytest-cov 7.0.0. Project requirements installed into repository-local `.venv`.

| Code tested | Command from `library-management/` | Result |
| --- | --- | --- |
| CI branch on current main | `python -m pytest -v --cov=app --cov-report=term-missing --cov-fail-under=90` | Exit 1: 33 passed, 1 failed; **85.80%** app coverage. |
| Ethan notification branch before Member B tests | Same coverage command | Exit 0: 41 passed, 1 xfailed; **97.78%** app coverage. |
| Ethan notification branch plus all six Member B tests | `python -m pytest -v` | Exit 0: **47 passed, 1 xfailed**. |
| Ethan notification branch plus all six Member B tests | Same coverage command | Exit 0: **47 passed, 1 xfailed; 99.44%** app coverage, 358/360 statements. |

`git diff --check` also passed. The initial sandboxed run emitted pytest cache permission warnings; the final full-suite and coverage runs used normal filesystem access and emitted no warnings. These percentages are local results.

Hosted CI was also inspected: https://github.com/MichelleBKelly/CISC327-Library-Management/actions/runs/43776873733 . Checkout, Python setup, and dependency installation succeeded; the test/coverage step failed with exit code 1. The run also warns that checkout v4 and setup-python v5 use deprecated Node 20 and are being run on Node 24; neither action failed. Hosted test logs were not downloaded, so the precise hosted test counts/percentage are not claimed here. PR #7 currently has no workflow on its branch because the CI PR remains separate and unmerged; its local validation is recorded above.

The existing failure on main is `test_returned_overdue_loan_fine_stops_at_the_return_date`: actual fine 1.00 versus expected 0.50. Ethan's #5 marks this documented A2 defect as strict xfail. His UI tests also cover the previously uncovered view routes. The CI threshold was not weakened and the application defect was not changed. Remaining uncovered statements after Member B tests: missing-member notification guard (`app/routes/loans.py:37`) and card-update self-skip (`app/routes/members.py:14`).

## Commits

- `a48a0bd` — Add coverage dependency and ignore generated coverage files (CI).
- `d091878` — Run project tests and enforce 90 percent coverage in GitHub Actions (CI).
- `6a89d40` — Test failed hold notification and return without a waiting member (tests).
- `ce5768b` — Cover missing book member loan and reservation API errors (tests).
- `1fda03a` — Document Member B validation results and required PR merge order.
- A final documentation commit records hosted CI status; obtain its hash with `git log -1 --oneline`.

## Required merge order and outstanding actions

1. Review and merge CI PR #6 into main first. Its checks currently expose main's existing fine failure and insufficient coverage, as measured above. If branch protection blocks that merge, the team must resolve the ordering policy; no checks were bypassed here.
2. Update Ethan's notification PR #5 from main, review it, then merge it. Its own PR description explicitly requires CI first. No approval or merge has been performed by this agent.
3. Update Michelle's test branch from the resulting main, retarget PR #7 to main, review it, then merge it. PR #7 initially targets Ethan's `feature/hold-available-notification` branch so its diff isolates Member B work. **Do not merge #7 into Ethan's branch.** If #5 is squash-merged, rebase only Michelle's commits onto updated main to avoid replaying Ethan's history.
4. Recheck hosted CI after updating each PR. No PR has been approved or merged.

## Command record

The following commands were executed; repeat invocations are grouped. File reads also included all application routes, models, templates, store, application factory, run script, styles, both READMEs, requirements, ignores, and every existing test. Files were edited with `apply_patch`.

Repository inspection:

```powershell
Get-Location
git status --short
git branch -avv
git log -12 --oneline --decorate
rg --files # with filters excluding environment/binary/Git internals
rg --files --hidden -g AGENTS.md -g '!.git' -g '!.venv'
git remote -v
git diff -- .gitignore requirements.txt
Get-Content README.md, library-management/README.md
Get-Content requirements.txt, library-management/requirements.txt, .gitignore, library-management/.gitignore
Get-Content library-management/tests/*.py
Get-Content library-management/app/routes/*.py
Get-Content library-management/app/models/*.py
Get-Content library-management/app/store.py, library-management/app/__init__.py
Get-Content library-management/app/templates/*.html, library-management/app/static/style.css, library-management/run.py
Get-ChildItem -Force
git ls-tree -r --name-only HEAD
git fetch origin --prune
git log origin/main..origin/feature/hold-available-notification --oneline
git diff origin/main...origin/feature/hold-available-notification --stat
git show origin/feature/hold-available-notification:library-management/app/routes/loans.py
git show origin/feature/hold-available-notification:library-management/tests/test_a3_ethan_lee.py
git diff origin/main...origin/feature/hold-available-notification -- library-management/tests/test_michelle_kelly.py
gh --version
gh pr list --state all --limit 30 --json number,title,state,headRefName,baseRefName,url,body
Get-Command gh, python, git -ErrorAction SilentlyContinue | Select-Object Name, Source
Invoke-RestMethod -Uri 'https://api.github.com/repos/MichelleBKelly/CISC327-Library-Management/pulls?state=all&per_page=30'
git config user.name
git config user.email
git config --get credential.helper
```

`gh` was unavailable. Initial sandboxed fetch/network attempts failed; the normal-access retry succeeded. GitHub API results showed #5 open and #1–#4 closed. No AGENTS.md was found in the repository.

Setup, branches, commits, and validation:

```powershell
git switch -c ci/github-actions --track origin/ci/github-actions
python --version
python -m pip show pytest pytest-cov Flask
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r library-management/requirements.txt pytest-cov
.\.venv\Scripts\python.exe -m pip install -r library-management/requirements.txt
git add .gitignore library-management/requirements.txt
git commit -m "Add coverage dependency and ignore generated coverage files"
git add .github/workflows/tests.yml
git commit -m "Run project tests and enforce 90 percent coverage in GitHub Actions"
# Each test invocation was run from library-management:
..\.venv\Scripts\python.exe -m pytest -v
..\.venv\Scripts\python.exe -m pytest -v --cov=app --cov-report=term-missing --cov-fail-under=90
git switch -c test/michelle-kelly-a3 origin/feature/hold-available-notification
git branch --unset-upstream
```

For initial local integration setup, CI commits were briefly cherry-picked onto the newly created test branch (`git cherry-pick a48a0bd d091878`). Before writing any tests, that new branch was recreated from Ethan's branch to keep the two PRs separate (`git switch ci/github-actions`, `git branch -f test/michelle-kelly-a3 origin/feature/hold-available-notification`, `git switch test/michelle-kelly-a3`, `git branch --unset-upstream`). No existing user branch/work was replaced. The temporary cherry-picks are not in either final branch history.

```powershell
Get-Content library-management/tests/test_a3_michelle_kelly.py
git add library-management/tests/test_a3_michelle_kelly.py
git commit -m "Test failed hold notification and return without a waiting member"
git commit -m "Cover missing book member loan and reservation API errors"
git diff --check
git diff origin/feature/hold-available-notification --stat
git diff ci/github-actions origin/main --stat
git log --oneline origin/feature/hold-available-notification..test/michelle-kelly-a3
git log --oneline origin/main..ci/github-actions
git diff origin/feature/hold-available-notification..test/michelle-kelly-a3 --name-only
git diff origin/main..ci/github-actions --name-only
git push -u origin ci/github-actions
git push -u origin test/michelle-kelly-a3
.\.venv\Scripts\python.exe .venv/a3_github.py
```

The ignored local helper reads existing Git Credential Manager credentials internally (`git credential fill`), checks for existing PRs with GET requests, and creates the two drafts with POST requests to the GitHub pulls API. Credentials are never printed or saved. Draft body files and helper are local files under ignored `.venv/`, not assignment source. Final handoff operations commit/push this report, inspect PR/check status, and preserve generated coverage data under `.venv/`; only generated cache directories from the initial failed cache writes are removed.

# Tasks

## 1. Workflow configuration

- [x] 1.1 In `openspec/config.yaml`, fill `context` with the pointers decision 6 lists (design principles in `INFECTIONS.md` → Principles; artifacts and repo docs in English; `README.md`/`INFECTIONS.md` updated in the same commit as code; one change per theme, one task per finding) and `rules.specs` with the naming rule of decision 5; verify `openspec instructions proposal --change "backlog-to-openspec" --json` returns the context and `openspec instructions specs --change "backlog-to-openspec" --json` returns the rule.

## 2. Documents

- [x] 2.1 In `CONTRIBUTING.md`, replace the "Open backlog" pointer (line ~32) with `openspec/changes/`, rewrite "Confirm scope before multi-part plans" to name a change instead of `proposals.md`, replace the Language bullet about `proposals.md` with one about OpenSpec artifacts, rewrite "Closing a proposal" as "Closing a change" (apply by tasks, update `INFECTIONS.md` in the same commit, `/opsx:archive`, archive commit `chore(openspec): archive <name>`, no numbers to cite) and add the granularity rule of decision 3, and change the PR checklist line to reference the change; verify `grep -n "proposals\.md" CONTRIBUTING.md` prints nothing (the word "proposals" survives as the OpenSpec artifact name).
- [x] 2.2 In `AGENTS.md`, replace the `proposals.md` bullet with the OpenSpec bullet (work starts as a change under `openspec/changes/`, artifacts in English, implemented changes are archived); verify `grep -n proposals AGENTS.md` prints nothing.
- [x] 2.3 In `README.md`, point the "open design backlog" line at `openspec/changes/`; verify `uv run pytest tests/test_doc_counts.py -q` passes and `grep -n proposals README.md` prints nothing.
- [x] 2.4 In `INFECTIONS.md`, change the one sentence under "Activate validator only when the substitute exists" so unactivated validators "live in an open change under `openspec/changes/`"; verify `grep -n 'proposals.md' INFECTIONS.md` prints nothing.
- [x] 2.5 `git rm proposals.md`; verify `git grep -n 'proposals\.md' -- ':!openspec/changes/archive' ':!tests/test_no_python_wording.py'` prints nothing (the test's docstring is historical narrative and stays).

## 3. Skill

- [x] 3.1 Rewrite `.claude/skills/backlog/SKILL.md` as the OpenSpec loop of decision 7, keeping the two rules it carried; verify the file names `openspec list`, `/opsx:apply` and `/opsx:archive` and no longer names `proposals.md` or `BACKLOG.md`.

## 4. Integration

- [x] 4.1 Run `uv run pytest -q` and `openspec validate --specs --strict`; verify both pass, then commit as `docs: the backlog is the OpenSpec change list` (one commit: config, docs, skill and the deletion belong together).

## Workflow follow-up

- Archive this change with `/opsx:archive`; it declares `skip_specs`, so there is no sync.

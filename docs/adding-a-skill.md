# Adding a skill (a new automation)

1. Open an issue that describes the chore, how often it happens, which site it uses, and
   what the user must confirm.
2. Put any deterministic logic (dates, rules, calculations) in `src/improving_assistant/`,
   and build it RED -> GREEN with tests in `tests/`. Expose it as an `ia.py` subcommand if the
   skill needs it.
3. Create `skills/<name>/SKILL.md`:

       ---
       name: <name>                 # must match the folder name (a test checks this)
       description: Use when ... . Does ... .   # the first sentence is the trigger
       argument-hint: "[optional args]"
       disable-model-invocation: true   # add it if the skill should only run when invoked by the user
       ---

       # Title
       ## Steps
       1. ...gather...
       2. ...show summary, wait for explicit OK...
       3. ...act, verify on screen...
       ## Rules
       - Never submit without OK. Never handle passwords or MFA.

   Refer to bundled files with `${CLAUDE_PLUGIN_ROOT}/...`.
4. If the skill drives a website, add or extend a screen map in `docs/<site>.md`: URLs, field
   labels, and what the confirmation looks like.
5. Add the skill name to `test_expected_skills_exist` in `tests/test_repo_contract.py`
   (RED first), then list it in the README.
6. Add a CHANGELOG entry and open a PR.

## Checklist

- [ ] Logic is in `src/`, built test-first
- [ ] SKILL.md frontmatter is valid and `name` matches the folder
- [ ] There is an explicit confirmation step before any write
- [ ] Screen map docs are updated
- [ ] README and CHANGELOG are updated

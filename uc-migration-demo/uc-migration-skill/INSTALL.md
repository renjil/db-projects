# Install the `uc-migration` skill (Claude Code)

This is a self-contained skill + slash commands. Two ways to use it.

## Option 1 - user-level (quickest, for practice)
Copy the skill and commands into your Claude Code config:

```bash
# from this folder (uc-migration-skill/)
mkdir -p ~/.claude/skills/uc-migration ~/.claude/commands
cp -R SKILL.md reference ~/.claude/skills/uc-migration/
cp commands/uc-*.md ~/.claude/commands/
```
Restart Claude Code. Verify: the skill appears when you ask about UC migration, and `/uc-analyse`, `/uc-plan`, `/uc-migrate`, `/uc-validate` are available.

## Option 2 - project-level (ship with a repo)
Place at the repo root so the team gets it on checkout:
```
<repo>/.claude/skills/uc-migration/SKILL.md
<repo>/.claude/skills/uc-migration/reference/*.md
<repo>/.claude/commands/uc-*.md
```

## Option 3 - package as a plugin (share at scale)
Wrap into a Claude Code plugin (`.claude-plugin/plugin.json` + `skills/` + `commands/`) and host it in an internal marketplace so engineers install with `/plugin marketplace add ...`. This mirrors how `databricks-agent-skills` ships skills + commands + hooks. Do this once the skill is proven.

## Before first use
1. Authenticate: `databricks auth login --host <workspace> --profile ffdemo`.
2. Fill in the **house conventions** in `SKILL.md` (target catalogs, schema mapping, external locations, group mapping).
3. Optionally run **UCX** assessment first for large estates; this skill can consume its output.

## Try it
```
/uc-analyse  ../legacy-pipelines/pattern_a_notebook_mounts
/uc-plan     ../legacy-pipelines/pattern_a_notebook_mounts
/uc-migrate  ../legacy-pipelines/pattern_a_notebook_mounts
/uc-validate hive_metastore.portfolio dev_catalog.portfolio
```

## Notes / honesty
- Commands are named `uc-*` to avoid clashing with other `/plan` etc. commands - rename if you prefer bare `/analyse`, `/plan`, `/migrate`.
- The skill is a **starter** seeded from two synthetic reference pipelines. Replace the legacy samples with real reference pipelines and tighten the house conventions to make it authoritative.
- `SYNC` is external-table-only; managed tables use `DEEP CLONE`/CTAS or UCX. The skill encodes this, but validate on your real tables before trusting it broadly.

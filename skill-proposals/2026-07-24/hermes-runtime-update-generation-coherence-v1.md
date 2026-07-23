---
name: hermes-runtime-update-generation-coherence-v1
description: Prevent Hermes updates from mutating dirty editable trees or live runtime environments; switch only through verified staged generations.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [update, installer, runtime, venv, dirty-tree, F10]
---

# hermes-runtime-update-generation-coherence-v1

## Use when

- Running CLI or Desktop self-update.
- Updating an editable checkout.
- Reinstalling Python or Node dependencies.
- Any Hermes process still holds files from the current runtime generation.

## Evidence

- GH #70211: repeated update attempts on a dirty editable tree can leave workspace manifests inconsistent.
- GH #70201: POSIX allows dependency files to change under a live interpreter, creating mixed old/new runtime state.

## Workflow

1. Resolve the installation kind: immutable release, managed checkout, or editable developer tree.
2. Run `git status --porcelain` for checkouts. If dirty, default to refuse. Do not auto-stash and continue unattended.
3. Detect live runtime holders on Linux, macOS, and Windows; include gateway, Desktop backend, cron workers, TUI, and MCP stdio children.
4. Build a new dependency generation in an isolated directory or venv; never rewrite the active generation in place.
5. Verify workspace manifest, lockfile, Python imports, Desktop build metadata, and runtime smoke tests in the staged generation.
6. Drain consumers, atomically switch the active generation pointer, then restart all consumers.
7. Record before/after generation IDs and a rollback pointer.
8. If any post-switch smoke fails, revert the pointer and restart the prior generation.

## Verification

- [ ] dirty tree refuses unattended update
- [ ] live holder blocks in-place mutation on all OSes
- [ ] staged generation imports are internally coherent
- [ ] workspace manifest and lockfile remain parseable
- [ ] all runtime consumers restart on one generation ID
- [ ] rollback returns to the prior generation

## Pitfalls

- POSIX file replacement success does not imply runtime safety.
- A surviving process may retain an old interface and lazy-load a new implementation.
- Repeated stash/pull/install cycles are not a transactional update protocol.

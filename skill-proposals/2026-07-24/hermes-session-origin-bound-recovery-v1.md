---
name: hermes-session-origin-bound-recovery-v1
description: Keep failed-prompt recovery, session navigation, archive cascades, and renderer restoration bound to the originating session identity.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [session, desktop, recovery, provenance, F9]
---

# hermes-session-origin-bound-recovery-v1

## Use when

- A provider request times out or exhausts retries.
- Desktop restores a failed prompt to the composer.
- Session navigation occurs from a non-chat panel.
- A compression lineage is archived.
- A large compressed session is rendered.

## Evidence

- GH #68358: failed prompt restoration can bind to the currently visible stale session instead of the originating session.
- GH #70185: archive cascade can hide a compression lineage without preview, audit, or undo.
- GH #70221: navigation can highlight a session without opening the chat context.
- GH #70206: duplicate tool-call identifiers can drive renderer failure loops on large compressed sessions.

## Workflow

1. Create an immutable recovery receipt at prompt submission: origin session ID, provider, model, profile, message ID, surface, and timestamp.
2. On failure, restore the prompt only into the originating session composer. If that session is unavailable, show an explicit recovery card; never silently bind to the current view.
3. Require session navigation to update route, active session store, runtime session mapping, and composer binding atomically.
4. Before archive cascade, resolve the full lineage and show affected session count and IDs.
5. Write an archive audit entry and issue an undo receipt.
6. Deduplicate tool-call identifiers before renderer mount; retain provenance by mapping duplicate source IDs to stable render IDs.
7. Verify provider/model do not change during recovery unless the user explicitly chooses a fallback.

## Verification

- [ ] timeout recovery stays on origin session
- [ ] switching visible session during timeout does not alter receipt
- [ ] navigation from Capabilities opens selected chat
- [ ] archive cascade previews all affected sessions
- [ ] archive undo restores lineage
- [ ] duplicate tool-call IDs do not crash renderer
- [ ] provider/model changes require explicit action

## Pitfalls

- “Current visible chat” is not authoritative session identity.
- Highlight state is not navigation completion.
- Compression lineage operations are multi-session mutations and need explicit scope.

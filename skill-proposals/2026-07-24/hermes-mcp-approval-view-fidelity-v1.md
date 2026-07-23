---
name: hermes-mcp-approval-view-fidelity-v1
description: Ensure MCP approval UI and model-delivered metadata are byte-faithful, reject concealment encodings, and require re-consent on tool-definition digest changes.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, approval, metadata, unicode, toc-tou, F7, F11]
---

# hermes-mcp-approval-view-fidelity-v1

## Use when

- MCP server is added, reloaded, or returns `tools/list` changes.
- Tool metadata comes from an external server.
- Approval UI renders tool name/description/schema.
- A sanitizer claims metadata is safe.

## Evidence

arXiv 2607.05744 reports:
- 8/8 tested metadata techniques reached model context.
- 4/8 evaded a representative string sanitizer.
- Unicode TAG-block concealment was the only tested technique that evaded both sanitizer and human approval rendering.
- 0/8 definition mutations forced re-approval.

## Workflow

1. Serialize the exact metadata object used for model prompt construction with deterministic JSON ordering and UTF-8 bytes.
2. Compute a digest over tool name, description, input schema, server identity, and protocol version.
3. Render the approval view from the same canonical byte buffer; never reconstruct a visually normalized second representation.
4. Reject Unicode code points U+E0000 through U+E007F or display escaped code-point notation requiring explicit approval.
5. Inspect all metadata surfaces: name, description, schema descriptions/defaults/enums, error text, and definition updates.
6. Detect namespace collisions with built-in or previously approved tools.
7. Persist the approved digest and compare it on every `tools/list` refresh.
8. If the digest changes, invalidate consent and require re-approval before exposing the tool to the model.

## Verification

- [ ] approval render digest equals model metadata digest
- [ ] TAG-block fixture rejected or visibly escaped
- [ ] schema default and enum risk fixture blocked
- [ ] colliding tool name fixture blocked
- [ ] tool error text treated as untrusted data
- [ ] post-approval description mutation triggers re-consent
- [ ] 25 benign tool descriptions remain accepted

## Pitfalls

- Visual equality is not byte equality.
- Keyword scanning alone is insufficient.
- `notifications/tools/list_changed` is cache invalidation, not authorization.
- Sanitizing only descriptions misses schema defaults, tool names, and errors.

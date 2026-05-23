---
name: letra-da-lei:pesquisa-legislacao
version: 0.1.0
description: >
  Use this skill when the user asks about Brazilian legislation, wants to look up
  a specific law or article, or needs a cited answer grounded in official statutory text.
allowed-tools:
  - mcp
---

# Brazilian Legal Research

Searches the Brazilian legal corpus via Letra da Lei and returns article-level results with verbatim text, citation IDs, and verified source links to official sources.

## Prerequisites

The `letradalei` MCP server must be connected. Verify it is available before starting. If not connected, inform the user and stop.

## When to use

- User asks what a Brazilian law says on any topic
- User wants to look up a specific article, code, or statute
- User needs a cited answer grounded in official statutory text
- User asks about rights, obligations, deadlines, or penalties under Brazilian law

## When not to use

- **Legal advice or predictions** — this skill retrieves legal text; a licensed Brazilian lawyer applies it to facts.

## Workflow

### 1. Understand the query

Identify whether the user is asking about:
- A specific law or article (exact lookup — use the `corpus` param with the `law_key`)
- A topic or concept (semantic search — use a natural language query)
- What laws are available — call `listar_legislacao_federal` first, then search

If the law key is uncertain, call `listar_legislacao_federal` to confirm before filtering with `corpus`.

### 2. Choose mode

- **fast** (default): exploratory questions, casual explanations, follow-ups on already-retrieved articles.
- **precise**: the result will be cited in a document (petition, contract, legal opinion), the user named a specific term or article number, or the question has legal consequence. When in doubt, prefer `precise`.

### 3. Search

Call `buscar_legislacao_federal` with the appropriate query, corpus (if known), and mode.

If results are empty or don't address the question, retry once with `mode="precise"` before concluding the corpus doesn't cover it.

### 4. Present results

- Quote the verbatim `text` field — do not paraphrase statute text.
- Always cite using the `source_url` returned so the user can verify against Planalto.gov.br.
- Use `citation_id` (e.g., `CF-1988-Art-5`) as the citation identifier.
- Tag all citations as `[Letra da Lei]`.
- Note `retrieved_at` so the user knows when the text was fetched.

### 5. Coverage gaps

If the question falls outside the corpus (confirmed by `listar_legislacao_federal` or zero results after a precise retry), tell the user clearly what isn't covered and where to look instead. Do not hallucinate statute text or cite articles not returned by the tool.

## Language

Respond in the language the user is using. When quoting article text, preserve the original Portuguese and translate if the user is in a different language.

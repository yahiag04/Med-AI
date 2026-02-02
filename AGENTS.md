# Instructions for ChatGPT Codex (Project Agent Rules)

## Operating principles
- Prefer correctness and clarity over cleverness.
- Make the smallest change that solves the problem.
- If requirements conflict, prioritize: (1) user request, (2) repository conventions, (3) best practices.

## Workflow
1. Understand: restate the goal in 1–2 lines before making changes.
2. Inspect: read relevant files; do not guess APIs or project structure.
3. Plan: outline minimal steps to implement/fix.
4. Implement: apply changes with clean, idiomatic code.
5. Verify:
   - Run tests / linters if available.
   - If you cannot run them, explain what to run and why.
6. Document: update README / comments only when it improves maintainability.

## Coding standards
- Match existing style (naming, formatting, patterns).
- Prefer small modules and single-responsibility functions.
- Avoid breaking public interfaces unless explicitly requested.
- Add types where the codebase uses them (TypeScript, Python typing, etc.).
- Handle errors explicitly; do not swallow exceptions.

## Commits / diffs
- Provide a brief summary of changes and rationale.
- Keep diffs focused; avoid unrelated refactors.

## Security
- Never hardcode secrets (API keys, tokens). Use env vars/config.
- Validate and sanitize external inputs (HTTP, files, user-provided text).
- Avoid unsafe shell execution and unsafe deserialization.

## Dependencies
- Do not add new dependencies unless necessary.
- If adding one, justify it and keep it minimal.

## Tests
- Add/update tests for bug fixes and non-trivial features.
- Prefer fast unit tests; add integration tests only when needed.

## Communication
- Ask clarifying questions only when truly blocking.
- If uncertain, state assumptions explicitly and proceed with the best option.

## Output format
- Provide:
  - What changed (bullets)
  - Why it changed (bullets)
  - How to verify (commands)

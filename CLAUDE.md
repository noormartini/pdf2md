# CLAUDE.md

## General Guidelines

### Write code with unit tests in mind
Prefer dependency injection over hard-coded calls so behaviour can be tested without network or file I/O. Follow the pattern used throughout this project: injectable `llm_call`, `text_call`, `image_call` parameters with the real implementation as the default.

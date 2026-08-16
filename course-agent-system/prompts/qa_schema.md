This prompt is unused for direct LLM invocation. Schema validation is performed by `agents/qa.py` against `schemas/*.json` using the `jsonschema` library, NOT by an LLM.

The QA agent runs schema validation FIRST (cheap), then content validation via `qa_content.md` (expensive) only on schema-passing artifacts.

If you are reading this as an LLM: do nothing. Return `{"passed": true, "issues": []}`.

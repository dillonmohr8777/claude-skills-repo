# Adding a new agent

Every agent follows the same pattern. To add one (e.g. `landing_page`):

## 1. Write the prompt

Create `prompts/landing_page.md`. Use Jinja2 syntax. Document expected input variables in a `## Inputs` section so renderers and reviewers can audit.

## 2. Write the schema (if structured output)

Create `schemas/landing.schema.json`. Use JSON Schema 2020-12. Reference it from the prompt.

## 3. Write the Python class

Create `agents/landing_page.py`:

```python
from agents.base import Agent

class LandingPage(Agent):
    agent_id = "landing_page"
    prompt_file = "landing_page.md"
    output_schema = None  # Markdown; or "landing.schema.json" if JSON
    response_format = "text"
    tier = "deep"
    temperature = 0.7

    def system(self) -> str:
        return "You are a direct-response copywriter..."

    # Optional: write_output, parse, custom helpers
```

## 4. Register tier in config

Add to `config/agents.yaml`:

```yaml
landing_page:
  tier: deep
  temperature: 0.7
```

## 5. Add to the workflow

Either chain into `workflows/mvp_pipeline.py` or create a new workflow file. Update `workflows/state.py` if you need a new stage.

## 6. Test

- Add a smoke test to `tests/test_prompts.py` with sample inputs.
- If the schema is structured, add a fixture and validation test to `tests/test_schemas.py`.

## 7. Document

Update the agent table in `README.md` and add a row in `docs/architecture.md` if behavior is non-obvious.

## Anti-patterns

- Hardcoding model IDs in the agent class. Use the tier system.
- Skipping the prompt file and inlining the prompt in Python. Prompts are the product; keep them in `prompts/`.
- Catching schema validation errors silently. The base class auto-retries once; if it fails twice, raise.
- Reading other agents' outputs by going through the filesystem when you could pass them as `inputs`.

"""Course Agent CLI.

Commands:
    course-agent new --slug <id> --title "..." --audience "..."   # scaffold a course folder
    course-agent run --slug <id>                                   # execute MVP pipeline
    course-agent export --slug <id>                                # re-export markdown
    course-agent status --slug <id>                                # show pipeline state
    course-agent re-render --slug <id> --lesson <lesson_id>        # rerun one lesson
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))  # so imports work whether invoked from repo root or as module

from workflows.state import initial_state, save_state, load_state
from exporters.markdown import export_course


COURSES_DIR = REPO_ROOT / "courses"


@click.group()
def cli() -> None:
    """Course Agent — autonomous course-creation pipeline."""


@cli.command()
@click.option("--slug", required=True, help="Kebab-case course id, e.g. ai-productivity-os")
@click.option("--title", required=True, help='Course title, e.g. "AI Productivity OS"')
@click.option("--audience", required=True, help="One-line audience description")
@click.option("--outcome", default="", help="Outcome promise (1 sentence)")
@click.option("--modules", default=5, type=int)
@click.option("--lessons-per-module", default=4, type=int)
@click.option("--target-hours", default=4.0, type=float)
@click.option("--price", default=97, type=int)
@click.option("--voice", default="Tim Ferriss-meets-Cal Newport", help="Voice reference")
@click.option("--qa-strictness", type=click.Choice(["lenient", "normal", "strict"]), default="normal")
def new(slug: str, title: str, audience: str, outcome: str, modules: int, lessons_per_module: int, target_hours: float, price: int, voice: str, qa_strictness: str) -> None:
    """Scaffold a new course folder with topic seed + initial state."""
    course_dir = COURSES_DIR / slug
    if course_dir.exists():
        raise click.ClickException(f"Course already exists: {course_dir}")
    course_dir.mkdir(parents=True)
    topic = {
        "id": slug,
        "title": title,
        "audience": audience,
        "outcome": outcome or f"By the end of this course, you can {title.lower()}.",
        "price_usd": price,
    }
    (course_dir / "topic.json").write_text(json.dumps(topic, indent=2))

    state = initial_state(
        slug,
        modules=modules,
        lessons_per_module=lessons_per_module,
        target_hours=target_hours,
        voice_reference=voice,
        qa_strictness=qa_strictness,
    )
    save_state(course_dir, state)
    click.echo(f"✓ Scaffolded {course_dir}")
    click.echo(f"   topic.json + state.json written")
    click.echo(f"   Run: course-agent run --slug {slug}")


@cli.command()
@click.option("--slug", required=True)
@click.option("--quiet", is_flag=True)
def run(slug: str, quiet: bool) -> None:
    """Execute the MVP pipeline end-to-end."""
    from workflows.mvp_pipeline import run as run_pipeline
    state = run_pipeline(slug, verbose=not quiet)
    click.echo(f"✓ Pipeline finished. Stage: {state['stage']}")


@cli.command()
@click.option("--slug", required=True)
def export(slug: str) -> None:
    """Re-export the Markdown bundle without re-running agents."""
    course_dir = COURSES_DIR / slug
    out = export_course(course_dir)
    click.echo(f"✓ Exported {out}")


@cli.command()
@click.option("--slug", required=True)
def status(slug: str) -> None:
    """Show course pipeline state."""
    state = load_state(COURSES_DIR / slug)
    click.echo(f"Course:   {state['course_id']}")
    click.echo(f"Stage:    {state['stage']}")
    click.echo(f"Updated:  {state['updated_at']}")
    click.echo("Checkpoints:")
    for k, v in state["human_checkpoints"].items():
        marker = "✓" if v["approved"] else "·"
        click.echo(f"  [{marker}] {k}")
    click.echo(f"Agent runs: {len(state.get('agent_runs', []))}")


@cli.command("re-render")
@click.option("--slug", required=True)
@click.option("--lesson", "lesson_id", required=True)
def re_render(slug: str, lesson_id: str) -> None:
    """Re-render a single lesson's script + slides + quiz."""
    from workflows.re_render import re_render_lesson
    re_render_lesson(slug, lesson_id)
    click.echo(f"✓ Re-rendered {lesson_id}")


if __name__ == "__main__":
    cli()

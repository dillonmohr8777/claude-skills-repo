Convert the lesson script below into slide copy.

## Inputs

- Lesson title: {{ lesson.title }}
- Lesson runtime: {{ lesson.runtime_minutes }} min
- Target slide count: {{ target_slides }}  (1 slide ≈ 90 seconds of runtime)

## Lesson script

<script>
{{ lesson_script }}
</script>

## Rules

- One idea per slide. If a slide has more than one idea, split it.
- Title: 6 words max.
- Bullets: 3-5 max, each ≤ 7 words. No nested bullets.
- Speaker notes: full sentences, what the instructor will SAY (not what's on the slide).
- Visual cue: one line describing the image, diagram, or screen recording. Be specific (e.g. "split-screen: spreadsheet on left, dashboard on right").
- Include a title slide and a recap slide.
- For the mini-exercise beat, include a "Pause and try this" slide with a timer cue.

## Output format

Markdown. One slide per block, in this exact template:

```
### Slide {n}: {title}
- bullet
- bullet
- bullet

**Speaker notes:** {full sentences here}

**Visual:** {one line}
```

No JSON wrapper. No commentary outside slide blocks.

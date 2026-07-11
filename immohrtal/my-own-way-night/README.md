# IMMOHRTAL — My Own Way (Official Video) · The Star Room Cut

Full-length 3:12 video built from Dillon's "MY OWN WAY — A Visual Story"
storyboards + two motion clips, edited in the grammar of Mac Miller's
"The Star Room (feat. Delusional Thomas)" MV
([`../reference/star-room-study.md`](../reference/star-room-study.md)).

## Sources

| | |
|---|---|
| `my-own-way.mp3` | full mix, 3:12 |
| `boards/sheet1-master40.png` | 40-panel narrative backbone (7×6 grid) |
| `boards/sheet2-heroes10.png` | 10 tall hero panels (5×2) |
| `boards/sheet3-alt36.png` | alternate takes / fill pool (7×6) |
| `clips/clip_a.mp4` | rooftop skyline sit (10s motion) |
| `clips/clip_b.mp4` | studio notebook + mic (10s motion) |

## How the cut works

- **Narrative backbone**: sheet1 panels 1→40 play in board order — dawn →
  city → studio → struggle → faith → grind → my own lane → full circle.
  The title cell opens cold; "THE END — this is just the beginning" closes.
- **Motion spliced throughout**: every ~3rd segment is a clip snippet
  (A/B alternating, staggered in-points, slow pan, ping-pong loop).
- **Heroes**: the 10 tall panels drift vertically every ~4th slot and act
  as the ghost layer that fades in/out over other segments.
- **Star Room grammar**: 0.8s cross-dissolves, slow push-ins, mirrored
  alter-ego doubles, escalation ramp (grain/ghosting/chroma bleed grow with
  runtime), cold open from black, long dissolve out into the end tag.
- **Grade**: `night_gold` — violet-ink shadows → warm amber highlights,
  bloom + chroma bleed. Tuned so the boards' gold 412 survives the night.
- **Panel prep**: gutter-detected slicing (labels live in the gutters and
  fall away), then two-stage lanczos upscale with unsharp + autocontrast
  to keep the halftone ink alive at 1080p.

## Build

```bash
python3 scripts/build_my_own_way.py   # needs ffmpeg, pillow, numpy
```

Writes `output/my-own-way-night-full.mp4` (CRF18 master) and
`output/my-own-way-night-full-web.mp4` (~8 Mbps delivery), plus
`scripts/edit.json` with the executed segment timeline.

## Deliverable

**[`dist/my-own-way-night.mp4`](dist/my-own-way-night.mp4)** (Git LFS) —
1080p24 delivery master, full track.

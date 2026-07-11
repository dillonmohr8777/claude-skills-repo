# IMMOHRTAL — 814 Blood (ft. King Keev) · The Star Room Cut

Night-side session modeled on Mac Miller's "The Star Room (feat. Delusional
Thomas)" MV. Grammar spec: [`../reference/star-room-study.md`](../reference/star-room-study.md).

## The grammar (vs. Notepad v2)

| | Notepad v2 (newsprint) | This cut (night) |
|---|---|---|
| Edit | beat-chop ~0.55s | 1.5–2.5 bar segments, **0.8s cross-dissolves** |
| Grade | sepia wash | ink→violet→magenta duotone, bloom, chroma bleed |
| Figures | static collage | **ghost stills** fade in/out mid-segment; mirrored doubles |
| Type | 8 chapter stamps | one declaration: **THE CMO ISN'T REAL** (~45%) + end tag |
| Arc | flat | escalation — grain/ghosting/bleed ramp with runtime |
| Open/close | title card | cold open from black, long dissolve out |

## What's here now

**[`dist/814-blood-night-teaser30.mp4`](dist/814-blood-night-teaser30.mp4)** —
1080p night cut of the 30s preview (the only 814 Blood audio in-repo).

## Full-length rebuild (when the mix lands)

Drop the full 2:20 mix at `814-blood.mp3` in this folder, then:

```bash
python3 scripts/build_night.py   # needs ffmpeg, pillow, numpy
```

The script auto-detects the full mix, re-plans segments on the 123 BPM bar
grid across 2:20, and writes `output/814-blood-night-full-web.mp4`. Nothing
else to change.

## Stills

`stills/` = Notepad v2 collage pool + `02_Campaigns/IMMOHRTAL/reference/photos`
(artist portrait, 814 lighthouse collage, lotus Erie/Pittsburgh). The night
duotone regrades everything, so daylight collage frames read as one interior.

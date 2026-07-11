# Reference Study — Mac Miller, "The Star Room (feat. Delusional Thomas)"

Source: https://youtu.be/Mos8UiWV6_g (2013, *Watching Movies with the Sound Off* era)

This is the grammar we mimic for the next IMMOHRTAL video. It is close to a
perfect reference for this project: the album is literally titled *Dance With
The Delusional*, and The Star Room is Mac's alter-ego track — Delusional
Thomas "featured" on his own song. Same move IMMOHRTAL is making with the
CMO-discipline / artist-instinct split.

## How the video goes

1. **Cold, quiet open.** The pitched-down Delusional Thomas voice runs over
   hazy footage before the beat lands. No titles, no branding — you arrive
   mid-dream.
2. **The world is one woozy interior.** Purple/pink practical lights, a
   psychedelic trashed hotel room, a dazzlingly lit room. Not locations — one
   headspace shot from different angles.
3. **Scenes dissolve, they don't cut.** Images "hazily transition from one to
   the next" — cross-dissolves, blur-throughs, double exposures. The edit
   floats on the beat instead of chopping on it. (Opposite of our Notepad v2
   beat-chop.)
4. **Ghost figures.** Cigarette-smoking Marilyn Monroe look-alikes appear and
   *disappear* mid-shot. Presence is unstable; people are apparitions.
5. **One blunt text declaration.** Mac sits casually under the words
   **"I'M NOT REAL."** That's the only typography that matters in the whole
   video — a single on-screen sentence doing the alter-ego thesis. No chapter
   stamps, no lower-thirds.
6. **The double.** The alter ego is staged visually — the same person split,
   mirrored, doubled, disputed ("Mac Miller disputes own realness" — SPIN).
7. **Slow escalation, not a drop.** It reads as "a bad trip": calm → woozy →
   unhinged → dissolves out with the warped outro. Energy curve is a long
   ramp, not verse/chorus spikes.

## Grammar extraction (what we copy)

| Element | Star Room | IMMOHRTAL translation |
|---|---|---|
| Cut style | Long takes, cross-dissolves, blur-throughs | 2.5–5s segments, 0.6–1.0s dissolves; hard cuts saved for 3–4 jolts |
| Camera | Slow push-ins, drift | Ken Burns zoom-IN only, slower easing than Notepad v2 |
| Grade | Crushed blacks, purple/pink neon glow, haze | Night duotone (ink black → magenta/violet), bloom/halation, lift the sepia entirely |
| Texture | VHS haze, soft focus | Chroma bleed, gaussian glow pass, grain that RAMPS over runtime |
| Figures | Appearing/disappearing Marilyns | Opacity-ghost stills — subjects fade in/out mid-segment |
| Alter ego | "I'M NOT REAL" + doubling | One declaration card (e.g. "I'M NOT REAL" register → ours), mirrored/offset double-exposure of the artist still |
| Typography | One statement, once | Kill chapter stamps. 1–3 sparse declarations max, centered, held long |
| Arc | Calm → bad trip → dissolve out | Warp/grain/ghosting intensity ramps section by section, ends on a long dissolve to black |

## Delta vs. Picking Up My Notepad v2

Notepad v2 was **daylight newsprint**: beat-chopped (~0.55s cuts), sepia,
torn-paper edges, persistent chapter stamps. The Star Room cut is its
**night-side inversion**: slow, dissolved, neon-dark, nearly wordless. Keep
the same stills-pipeline architecture (`build_v2.py`), change the grammar:

- `detect_cuts` → sparse segment boundaries (phrase-level, not onset-level)
- add dissolve rendering (overlap frames between segments, alpha blend)
- `sepia()` → `night_duotone()` (crush + magenta/violet split-tone + bloom)
- `torn_edge_mask` → retire; replace with ghost/double-exposure compositor
- `CHAPTERS` → 1–3 `DECLARATIONS` (single centered statements, long fades)
- escalation parameter: warp/grain scales with `t / duration`

## Track fit (candidates)

- **814 Blood (ft. King Keev)** — the feature-track mirror; vault notes
  already call it a "night-world track." 2:20, 123 BPM. Only a 30s preview
  in-repo; full mix needed from Dillon.
- **Dance with the Delusional (ft. Ted Moon)** — strongest thematic mirror
  (the literal Delusional track). No audio in-repo yet.
- **No Way Out** — album-opener mirror (Star Room opens *WMWTSO*). No audio
  in-repo yet.
- **Picking Up My Notepad (v3 night cut)** — only track with full audio in
  hand (2:52); could build the Star Room treatment today.

Sources: [SPIN](https://www.spin.com/2013/10/mac-miller-the-star-room-video/),
[EARMILK](https://earmilk.com/2013/10/03/mac-miller-the-star-room-feat-delusional-thomas-video/),
[Zumic](https://zumic.com/star-room-mac-miller-ft-delusional-thomas-youtube-official-video),
[IMDb](https://www.imdb.com/title/tt11482000/).
